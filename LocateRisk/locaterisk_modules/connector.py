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
            data = []
            try:
                response = requests.get(
                    f"{self.module.configuration.report_url}/{self.module.configuration.scan_id}/csv",
                    headers={"Authorization": f"Bearer {self.module.configuration.api_key}"},
                )
                response.raise_for_status()

                # Parse the CSV body into a list of dicts (header row → keys)
                csv_text = response.text
                reader = csv.DictReader(io.StringIO(csv_text), delimiter=";")
                rows = list(reader)

            except requests.RequestException as error:
                self.log_exception(error, message="Error fetching data from Locaterisk API")
            except csv.Error as error:
                self.log_exception(error, message="Error parsing CSV from Locaterisk API")

            # Process collected data (if needed)
            batch_of_events = []
            for row in rows:
                row["source"] = "Locaterisk"
                batch_of_events.append(json.dumps(row))

            # Push events to Sekoia platform
            if batch_of_events:
                self.log(
                    message=f"{len(batch_of_events)} events collected",
                    level="info",
                )
                self.push_events_to_intakes(events=batch_of_events)

            # Wait for the next polling interval
            time.sleep(self.configuration.polling_interval * 60)
