#!/usr/bin/env python3
"""Create or update the ElevenLabs agent behind the button "Anruf annehmen".

    ELEVENLABS_API_KEY=... python3 voice/agent_anlegen.py

The agent only talks. Everything it does goes through three client tools that run in the
page (docs/app/index.html): list what waits, approve, reject. The rules stay in the page,
so the agent cannot approve anything the signed-in person may not approve.
Writes the agent id to voice/agent.json. The id is public by design (it sits in the page).
"""
import json, os, sys, urllib.error, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
AGENT_FILE = HERE / "agent.json"
VOICE = "rKiu7lQ4c5P3az3745s3"   # Carla Blum, German
NAME = "adh-budget-freigabe-anruf"

PROMPT = """# Personality
Du bist der Freigabe-Assistent eines mittelständischen Unternehmens. Sachlich, knapp, freundlich. Du sprichst Deutsch und siezt.

# Environment
Du rufst eine Führungskraft an, auf deren Freigabe Budgetanträge warten. Die Person heißt {{name}} und hat die Rolle {{rolle}}. Sie hört dich am Telefon und sieht keinen Bildschirm. Firma, Personen und Anträge sind Beispieldaten einer Vorführung.

# Tone
- Kurze Sätze, ein Antrag nach dem anderen.
- Beträge als gesprochene Zahl in Euro, Antragsnummern Ziffer für Ziffer.
- Keine Aufzählungszeichen, keine Sonderzeichen.

# Goal
1. Ruf zuerst offene_freigaben auf. This step is important. Nenne nie einen Antrag, der nicht in dieser Antwort steht.
2. Wartet nichts, sag das in einem Satz und verabschiede dich.
3. Lies den ersten Antrag vor: Nummer, Gegenstand, Betrag, wer ihn gestellt hat, und ob die Person in Vertretung entscheidet. Frag dann: freigeben, ablehnen oder später entscheiden?
4. Bevor du freigeben oder ablehnen aufrufst, wiederhole die Entscheidung mit Nummer und Betrag und warte auf ein klares Ja. This step is important. Ohne klares Ja rufst du kein Werkzeug auf.
5. Eine Ablehnung braucht eine Begründung. Frag danach und gib sie wörtlich an ablehnen weiter.
6. Sag nach jedem Werkzeug, was das Werkzeug geantwortet hat, mit eigenen Worten und ohne etwas hinzuzufügen. Dann der nächste Antrag.
7. Am Ende fasse in einem Satz zusammen, was entschieden wurde, und verabschiede dich.

# Guardrails
Du entscheidest nichts selbst und rätst nie zu einer Entscheidung. Du änderst keine Grenzen, Rollen oder Vertretungen. Meldet ein Werkzeug, dass etwas nicht geht, sagst du genau das. Fragen, die nichts mit den wartenden Anträgen zu tun haben, lehnst du höflich ab."""


def tool(name, description, params=None, required=()):
    return {"type": "client", "name": name, "description": description, "expects_response": True, "response_timeout_secs": 20,
            "parameters": {"type": "object", "properties": params or {}, "required": list(required)}}


TOOLS = [
    tool("offene_freigaben", "Liefert die Anträge, die gerade auf die Freigabe der angerufenen Person warten."),
    tool("freigeben", "Gibt einen Antrag frei. Nur nach einem klaren Ja der Person aufrufen.",
         {"nummer": {"type": "string", "description": "Antragsnummer, zum Beispiel BA-1044"}}, ["nummer"]),
    tool("ablehnen", "Lehnt einen Antrag ab. Nur nach einem klaren Ja und mit Begründung aufrufen.",
         {"nummer": {"type": "string", "description": "Antragsnummer, zum Beispiel BA-1044"},
          "grund": {"type": "string", "description": "Begründung der Person, wörtlich"}}, ["nummer", "grund"]),
]


def api(path, data=None, method=None):
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        sys.exit("ELEVENLABS_API_KEY is not set")
    req = urllib.request.Request("https://api.elevenlabs.io" + path, data=json.dumps(data).encode() if data is not None else None,
                                 headers={"xi-api-key": key, "content-type": "application/json"},
                                 method=method or ("POST" if data is not None else "GET"))
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        sys.exit(f"ElevenLabs {e.code}: {e.read()[:500].decode(errors='replace')}")


def main():
    old = json.loads(AGENT_FILE.read_text()) if AGENT_FILE.exists() else {}
    prompt = {"prompt": PROMPT, "temperature": 0.2, "tools": TOOLS, "timezone": "Europe/Berlin"}
    if old.get("agent_id"):   # the model chosen in the ElevenLabs UI stays as it is
        prompt["llm"] = api(f"/v1/convai/agents/{old['agent_id']}")["conversation_config"]["agent"]["prompt"].get("llm")
    else:
        prompt["llm"] = "gemini-2.5-flash"
    payload = {
        "name": NAME,
        "conversation_config": {
            "agent": {"first_message": "Guten Tag, hier ist der Freigabe-Assistent. Ich schaue kurz nach, was auf Ihre Freigabe wartet.",
                      "language": "de", "prompt": prompt,
                      "dynamic_variables": {"dynamic_variable_placeholders": {"name": "Hanna Vogt", "rolle": "Bereichsleitung Betrieb"}}},
            "tts": {"voice_id": VOICE, "model_id": "eleven_flash_v2_5"},
            "conversation": {"max_duration_seconds": 300}},
        "platform_settings": {
            "call_limits": {"agent_concurrency_limit": 2, "daily_limit": 40},   # the page is public: bound the cost
            "overrides": {"conversation_config_override": {"conversation": {"text_only": True}}}},
    }
    if old.get("agent_id"):
        api(f"/v1/convai/agents/{old['agent_id']}", payload, "PATCH"); agent_id = old["agent_id"]
    else:
        agent_id = api("/v1/convai/agents/create", payload)["agent_id"]
    AGENT_FILE.write_text(json.dumps({"agent_id": agent_id, "name": NAME}, indent=1) + "\n")
    print(agent_id)


if __name__ == "__main__":
    main()
