#!/usr/bin/env python3

import argparse
import requests
import sox
import os

def synthesize(output, text):
	url = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'
	headers = {
	'Authorization': 'Api-Key ' + '',
	}

	data = {
		'text': text,
		'lang': 'ru-RU',
		'voice': 'alena',
		'emotion': 'neutral',
		'format': 'lpcm',
		'sampleRateHertz': '8000'
	}
	with requests.post(url, headers=headers, data=data, stream=True, verify=False) as resp:

		if resp.status_code != 200:
			raise RuntimeError("Invalid response received: code: %d, message: %s" % (resp.status_code, resp.text))
		for chunk in resp.iter_content(chunk_size=None):
			yield chunk

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--text", required=True, help="Text for synthesize")
	parser.add_argument("--output", required=True, help="Output file name")
	args = parser.parse_args()
	with open(args.output, "wb") as f:
		for audio_content in synthesize(args.output, args.text):
			f.write(audio_content)
	tfm = sox.Transformer()
	tfm.set_input_format(file_type='raw', rate=8000, bits=16, channels=1, encoding='signed-integer')
	tfm.build(args.output, args.output+'.wav')
	os.remove(args.output)
	
