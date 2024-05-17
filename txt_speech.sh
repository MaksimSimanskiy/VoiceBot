#!/bin/bash

if [ -z "$1" ] || [ -z "$2" ]
then
  echo "Usage: ./speech.sh <text> <filename>"
  exit 1
fi

json='{"text": "'"$1"'","output_audio_spec":{
      "rawAudio": {
        "audioEncoding": "LINEAR16_PCM",
        "sampleRateHertz": 8000
      }
    }, "hints": [{"speed": 1}, {"voice": "b1gs9a5ant07jps2s9d8"}]}'

echo $json | \
jq -c '.' | \
~/go/bin/grpcurl -H "Authorization: Api-Key AQVNzkfa052DgfDgk7isPgb_JMMYF2MMcxsaPJrK" \
        -d @ tts.api.cloud.yandex.net:443 speechkit.tts.v3.Synthesizer/UtteranceSynthesis | \
jq -r '.audioChunk.data' | base64 -d > /tmp/$2$2.wav
sox -r 8000 -t raw -e signed-integer -b 16 -c 1 /tmp/$2$2.wav /tmp/$2.wav
rm -f "/tmp/$2$2.wav"
chmod a+rwx "/tmp/$2.wav"
/tmp/cleaner.sh
#sleep 60 && rm -f /tmp/$2.wav
echo "File saved as /tmp/$2.wav"

