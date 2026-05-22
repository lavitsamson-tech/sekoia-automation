import csv
import io
import json
import time
from pydantic import Field
from sekoia_automation.connector import Connector, DefaultConnectorConfiguration
import requests

from . import LocateriskModule


class LocateriskConnectorConfiguration(DefaultConnectorConfiguration):
    polling_interval: int = Field(5, description="Polling interval in minutes")


class LocateriskConnector(Connector):
    module: LocateriskModule
    configuration: LocateriskConnectorConfiguration

    def run(self):
        self.log(message="Start fetching events", level="info")

        while self.running:
            self.log("Polling Locaterisk API...", level="info")

            # Fetch data from the Locaterisk API
            try:
                response = requests.get(
                    f"{self.module.configuration.report_url}/{self.module.configuration.scan_id}/csv",
                    headers={"Authorization": f"Bearer {self.module.configuration.api_key}"},
                )
                response.raise_for_status()

                response.encoding = "utf-8-sig"  # strip BOM
                csv_text = response.text

                # Use csv.reader to parse rows correctly, respecting quoted multi-line fields.
                reader = csv.reader(io.StringIO(csv_text), delimiter=";", quotechar='"')

                rows = list(reader)

            except requests.RequestException as error:
                self.log_exception(error, message="Error fetching data from Locaterisk API")
            except csv.Error as error:
                self.log_exception(error, message="Error parsing CSV from Locaterisk API")

            if len(rows) < 2:
                self.log("No data rows in response", level="info")
                time.sleep(self.configuration.polling_interval * 60)
                continue

            header = rows[0]  # we discard this; parser doesn't need it
            data_rows = rows[1:]

            # Re-serialize each row as a single CSV line, replacing embedded newlines
            # in field values so Sekoia receives ONE line per event.
            batch_of_events = []
            for row in data_rows:
                # Replace embedded newlines within each field with a placeholder
                # that the parser can split on later
                cleaned_fields = [field.replace("\n", "\\n").replace("\r", "") for field in row]

                output = io.StringIO()
                writer = csv.writer(output, delimiter=";", quotechar='"', quoting=csv.QUOTE_ALL)
                writer.writerow(cleaned_fields)
                line = output.getvalue().rstrip("\r\n")  # strip the trailing newline writer adds
                batch_of_events.append(line)

            # Push events to Sekoia platform
            if batch_of_events:
                self.log(
                    message=f"{len(batch_of_events)} events collected",
                    level="info",
                )
                self.push_events_to_intakes(events=batch_of_events)

            # Wait for the next polling interval
            time.sleep(self.configuration.polling_interval * 60)
