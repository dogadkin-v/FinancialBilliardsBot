import os
import json
from os import makedirs
import datetime

class DataWorker:
    def create(self, name):
        makedirs('_data', exist_ok=True)
        open(f'_data/{name}.json', 'w')

    def save(self, name, data):
        fileData = {
            'data': data
        }

        for item in fileData['data']:
            if 'debt' in item:
                item['debt'] = {date.isoformat(): amount for date, amount in item['debt'].items()}

        with open(f'_data/{name}.json', 'w', encoding='utf8') as outfile:
            json.dump(fileData, outfile, ensure_ascii=False, indent=4)

    def load(self, name):
        with open(f'_data/{name}.json', encoding='utf-8') as json_file:
            file = json.load(json_file)
            for item in file['data']:
                if 'debt' in item:
                    item['debt'] = {datetime.date.fromisoformat(date): amount for date, amount in item['debt'].items()}
            data = file['data']
            return data

    def remove(self, name):
        os.remove(f'_data/{name}.json')