import json
import base64
import os
from flask import Flask, render_template, request, jsonify
import anthropic

app = Flask(__name__)
client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/translate', methods=['POST'])
def translate():
    data = request.get_json()
    image_data = data.get('image', '')

    if ',' in image_data:
        media_type_part, image_data = image_data.split(',', 1)
        media_type = media_type_part.split(':')[1].split(';')[0] if ':' in media_type_part else 'image/jpeg'
    else:
        media_type = 'image/jpeg'

    try:
        message = client.messages.create(
            model='claude-sonnet-4-6',
            max_tokens=1024,
            messages=[{
                'role': 'user',
                'content': [
                    {
                        'type': 'image',
                        'source': {
                            'type': 'base64',
                            'media_type': media_type,
                            'data': image_data,
                        }
                    },
                    {
                        'type': 'text',
                        'text': (
                            'Analysiere dieses Bild und extrahiere allen sichtbaren Text.\n'
                            'Übersetze ihn dann vollständig auf Deutsch.\n\n'
                            'Antworte NUR mit diesem JSON (kein Markdown, keine Erklärung):\n'
                            '{\n'
                            '  "erkannte_sprache": "Name der Originalsprache",\n'
                            '  "original": "Kompletter Originaltext aus dem Bild",\n'
                            '  "uebersetzung": "Vollständige deutsche Übersetzung",\n'
                            '  "kein_text": false\n'
                            '}\n\n'
                            'Falls kein lesbarer Text vorhanden:\n'
                            '{"erkannte_sprache":"","original":"","uebersetzung":"","kein_text":true}'
                        )
                    }
                ]
            }]
        )

        raw = message.content[0].text.strip()
        # Strip markdown code fences if present
        if raw.startswith('```'):
            raw = raw.split('\n', 1)[1]
            raw = raw.rsplit('```', 1)[0]

        result = json.loads(raw)
        return jsonify({'success': True, **result})

    except json.JSONDecodeError:
        return jsonify({'success': True, 'erkannte_sprache': '', 'original': '', 'uebersetzung': raw, 'kein_text': False})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5003))
    app.run(host='0.0.0.0', port=port, debug=False)
