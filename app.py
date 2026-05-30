import json
import os
from flask import Flask, render_template, request, jsonify
import anthropic

app = Flask(__name__)
client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))


def call_claude(image_data, media_type, prompt, max_tokens=2048):
    message = client.messages.create(
        model='claude-haiku-4-5-20251001',
        max_tokens=max_tokens,
        messages=[{
            'role': 'user',
            'content': [
                {
                    'type': 'image',
                    'source': {'type': 'base64', 'media_type': media_type, 'data': image_data}
                },
                {'type': 'text', 'text': prompt}
            ]
        }]
    )
    raw = message.content[0].text.strip()
    if '```' in raw:
        parts = raw.split('```')
        raw = parts[1]
        if raw.startswith('json'):
            raw = raw[4:]
        raw = raw.strip()
    start, end = raw.find('{'), raw.rfind('}')
    if start != -1 and end != -1:
        raw = raw[start:end+1]
    return json.loads(raw)


def parse_image(data):
    image_data = data.get('image', '')
    if ',' in image_data:
        part, image_data = image_data.split(',', 1)
        media_type = part.split(':')[1].split(';')[0] if ':' in part else 'image/jpeg'
    else:
        media_type = 'image/jpeg'
    return image_data, media_type


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/translate', methods=['POST'])
def translate():
    try:
        image_data, media_type = parse_image(request.get_json())
        result = call_claude(image_data, media_type, (
            'Analysiere dieses Bild. Erkenne alle Textstellen und übersetze sie auf Deutsch.\n'
            'Gib für jeden Textblock seine ungefähre Position im Bild als Prozentwert an.\n\n'
            'Antworte NUR mit diesem JSON (kein Markdown):\n'
            '{\n'
            '  "sprache": "Name der Originalsprache",\n'
            '  "blocks": [\n'
            '    {"original":"Text","deutsch":"Übersetzung","x":10,"y":20,"breite":45,"hoehe":6}\n'
            '  ]\n'
            '}\n'
            'x/y = linke obere Ecke in % der Bildbreite/höhe. breite/hoehe in %.\n'
            'Falls kein Text: {"sprache":"","blocks":[],"kein_text":true}'
        ))
        return jsonify({'success': True, **result})
    except json.JSONDecodeError as e:
        return jsonify({'success': False, 'error': f'JSON-Fehler: {e}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/landmark', methods=['POST'])
def landmark():
    try:
        image_data, media_type = parse_image(request.get_json())
        result = call_claude(image_data, media_type, (
            'Analysiere dieses Bild. Erkenne das abgebildete Gebäude, Denkmal oder die Sehenswürdigkeit.\n\n'
            'Antworte NUR mit diesem JSON (kein Markdown, auf Deutsch):\n'
            '{\n'
            '  "gefunden": true,\n'
            '  "name": "Offizieller Name",\n'
            '  "typ": "z.B. Kirche / Schloss / Denkmal / Museum",\n'
            '  "ort": "Stadt, Land",\n'
            '  "kurzbeschreibung": "2-3 Sätze was das ist",\n'
            '  "geschichte": "3-5 Sätze zur Geschichte",\n'
            '  "fakten": ["Fakt 1", "Fakt 2", "Fakt 3"],\n'
            '  "besuchertipp": "Praktischer Tipp für Besucher"\n'
            '}\n\n'
            'Falls kein Gebäude/Sehenswürdigkeit erkennbar:\n'
            '{"gefunden":false,"name":"","typ":"","ort":"","kurzbeschreibung":"Kein bekanntes Gebäude erkannt.","geschichte":"","fakten":[],"besuchertipp":""}'
        ), max_tokens=1500)
        return jsonify({'success': True, **result})
    except json.JSONDecodeError as e:
        return jsonify({'success': False, 'error': f'JSON-Fehler: {e}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/plant', methods=['POST'])
def plant():
    try:
        image_data, media_type = parse_image(request.get_json())
        result = call_claude(image_data, media_type, (
            'Analysiere dieses Bild und erkenne die abgebildete Pflanze, Blume oder den Baum.\n\n'
            'Antworte NUR mit diesem JSON (kein Markdown, auf Deutsch):\n'
            '{\n'
            '  "gefunden": true,\n'
            '  "name": "Deutscher Alltagsname",\n'
            '  "wissenschaftlich": "Lateinischer Name",\n'
            '  "typ": "z.B. Baum / Strauch / Blume / Zimmerpflanze / Kräuter",\n'
            '  "herkunft": "Ursprungsregion",\n'
            '  "beschreibung": "2-3 Sätze zur Pflanze",\n'
            '  "pflege": ["Pflegetipp 1", "Pflegetipp 2", "Pflegetipp 3"],\n'
            '  "giftig_menschen": "ja / nein / teilweise – kurze Erklärung",\n'
            '  "giftig_katzen": "ja / nein / teilweise – kurze Erklärung was passiert",\n'
            '  "fakten": ["Fakt 1", "Fakt 2"],\n'
            '  "erkennungssicherheit": "hoch / mittel / niedrig"\n'
            '}\n\n'
            'Falls keine Pflanze erkennbar:\n'
            '{"gefunden":false,"name":"","wissenschaftlich":"","typ":"","herkunft":"","beschreibung":"Keine Pflanze erkannt.","pflege":[],"giftig_menschen":"","giftig_katzen":"","fakten":[],"erkennungssicherheit":"niedrig"}'
        ), max_tokens=1500)
        return jsonify({'success': True, **result})
    except json.JSONDecodeError as e:
        return jsonify({'success': False, 'error': f'JSON-Fehler: {e}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/repair', methods=['POST'])
def repair():
    try:
        image_data, media_type = parse_image(request.get_json())
        result = call_claude(image_data, media_type, (
            'Analysiere dieses Bild. Erkenne das Objekt, den Schaden oder die Fehlermeldung.\n'
            'Gib eine praktische Reparaturanleitung auf Deutsch.\n\n'
            'Antworte NUR mit diesem JSON (kein Markdown):\n'
            '{\n'
            '  "gefunden": true,\n'
            '  "objekt": "Was ist das (z.B. Wasserhahn, Autoreifen, Waschmaschine)",\n'
            '  "problem": "Was ist das erkannte Problem/der Schaden",\n'
            '  "ursachen": ["Mögliche Ursache 1", "Ursache 2"],\n'
            '  "schritte": ["Schritt 1", "Schritt 2", "Schritt 3"],\n'
            '  "werkzeug": ["Werkzeug 1", "Werkzeug 2"],\n'
            '  "schwierigkeit": "einfach / mittel / schwer",\n'
            '  "profi_noetig": false,\n'
            '  "profi_begruendung": "Nur falls Profi nötig: Warum",\n'
            '  "kosten_schaetzung": "z.B. 0€ (selbst) / 20-50€ (Teile) / 100-300€ (Werkstatt)",\n'
            '  "sicherheitshinweis": "Wichtiger Hinweis falls gefährlich, sonst leer lassen"\n'
            '}\n\n'
            'Falls kein Problem/Objekt erkennbar:\n'
            '{"gefunden":false,"objekt":"","problem":"Kein Schaden oder Objekt erkannt.","ursachen":[],"schritte":[],"werkzeug":[],"schwierigkeit":"","profi_noetig":false,"profi_begruendung":"","kosten_schaetzung":"","sicherheitshinweis":""}'
        ), max_tokens=1500)
        return jsonify({'success': True, **result})
    except json.JSONDecodeError as e:
        return jsonify({'success': False, 'error': f'JSON-Fehler: {e}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5003))
    app.run(host='0.0.0.0', port=port, debug=False)
