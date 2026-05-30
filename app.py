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
            model='claude-haiku-4-5-20251001',
            max_tokens=2048,
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
                            'Analysiere dieses Bild. Erkenne alle Textstellen und übersetze sie auf Deutsch.\n'
                            'Gib für jeden Textblock seine ungefähre Position im Bild als Prozentwert an.\n\n'
                            'Antworte NUR mit diesem JSON (kein Markdown, keine Erklärung):\n'
                            '{\n'
                            '  "sprache": "Name der Originalsprache",\n'
                            '  "blocks": [\n'
                            '    {\n'
                            '      "original": "Originaltext des Blocks",\n'
                            '      "deutsch": "Deutsche Übersetzung",\n'
                            '      "x": 10,\n'
                            '      "y": 20,\n'
                            '      "breite": 45,\n'
                            '      "hoehe": 6\n'
                            '    }\n'
                            '  ]\n'
                            '}\n'
                            'x/y = linke obere Ecke in % der Bildbreite/höhe. breite/hoehe in %.\n'
                            'Jeden zusammenhängenden Textblock als eigenen Eintrag.\n\n'
                            'Falls kein Text vorhanden:\n'
                            '{"sprache":"","blocks":[],"kein_text":true}'
                        )
                    }
                ]
            }]
        )

        raw = message.content[0].text.strip()

        # Code-Fence entfernen (```json ... ``` oder ``` ... ```)
        if '```' in raw:
            parts = raw.split('```')
            # Nimm den Teil nach dem ersten ``` (Index 1), entferne optionalen "json"-Bezeichner
            raw = parts[1]
            if raw.startswith('json'):
                raw = raw[4:]
            raw = raw.strip()

        # Erstes { bis letztes } extrahieren (ignoriert Text davor/danach)
        start = raw.find('{')
        end   = raw.rfind('}')
        if start != -1 and end != -1:
            raw = raw[start:end+1]

        result = json.loads(raw)
        return jsonify({'success': True, **result})

    except json.JSONDecodeError as e:
        # Im Fehlerfall die Rohausgabe zurückgeben um zu debuggen
        raw_preview = locals().get('raw', '')[:300]
        return jsonify({'success': False, 'error': f'JSON-Fehler: {e} | Antwort: {raw_preview}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5003))
    app.run(host='0.0.0.0', port=port, debug=False)
