
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import json
eval_schema = {
  "type": "object",
  "description": "Die Bewertung des Dialogs",
  "properties": {
    "Wirksamkeit bei der Reduktion kognitiver Verzerrungen": {
      "type": "integer",
      "description": "Wirksamkeit bei der Reduktion kognitiver Verzerrungen - Erkennung der Verzerrungen - Erfolgreiche Intervention - Messbare Veränderung im Gesprächsverlauf und ist zu bewerten von 1 bis 5: \n\n1 Stern: Sehr schlecht – Kognitive Verzerrungen werden nicht erkannt oder vollständig ignoriert.\n2 Sterne: Schlecht – Einige Verzerrungen werden erkannt, jedoch unvollständig oder fehlerhaft.\n3 Sterne: Befriedigend – Die meisten Verzerrungen werden erkannt, aber es gibt Verbesserungspotenzial.\n4 Sterne: Gut – Verzerrungen werden klar und größtenteils genau identifiziert.\n5 Sterne: Ausgezeichnet – Alle Verzerrungen werden präzise und umfassend erkannt."
    },
    "Adaptivität und Individualisierung": {
      "type": "integer",
      "description": "Adaptivität und Individualisierung - Anpassung an individuelle Bedürfnisse - Flexibilität bei verschiedenen Verzerrungsarten - Berücksichtigung persönlicher Umstände und ist zu bewerten von 1 bis 5: \n\n1 Stern: Sehr schlecht – Keine Anpassung an individuelle Umstände oder Bedürfnisse.\n2 Sterne: Schlecht – Eingeschränkte Anpassung; viele Bedürfnisse bleiben unberücksichtigt.\n3 Sterne: Befriedigend – Angemessene Anpassung mit einigen Lücken.\n4 Sterne: Gut – Gute Flexibilität und Individualisierung mit geringfügigen Verbesserungsmöglichkeiten.\n5 Sterne: Ausgezeichnet – Hervorragende Anpassung an individuelle Umstände und Bedürfnisse."
    },
    "Therapeutische Allianz": {
      "type": "integer",
      "description": "Therapeutische Allianz - Empathie und Verständnis - Vertrauensaufbau - Collaborative Approach und ist zu bewerten von 1 bis 5: \n\n1 Stern: Sehr schlecht – Keine Empathie oder Vertrauensaufbau.\n2 Sterne: Schlecht – Begrenzte Empathie und ein schwaches Vertrauen.\n3 Sterne: Befriedigend – Angemessenes Verständnis und Vertrauen, aber mit Verbesserungspotenzial.\n4 Sterne: Gut – Gute Empathie und kooperativer Ansatz.\n5 Sterne: Ausgezeichnet – Höchstmaß an Empathie, Vertrauen und Zusammenarbeit."
    },
    "Therapeutische Kompetenz": {
      "type": "integer",
      "description": "Therapeutische Kompetenz - Präzise Identifikation von Verzerrungen - Effektive Interventionsauswahl - Professionelle Gesprächsführung und ist zu bewerten von 1 bis 5: \n\n1 Stern: Sehr schlecht – Verzerrungen werden nicht erkannt, und Interventionen sind ineffektiv.\n2 Sterne: Schlecht – Unzureichende Präzision bei der Identifikation oder Auswahl der Intervention.\n3 Sterne: Befriedigend – Akzeptable Kompetenz mit deutlichem Verbesserungspotenzial.\n4 Sterne: Gut – Kompetente Identifikation und Interventionen mit minimalen Schwächen.\n5 Sterne: Ausgezeichnet – Höchste Professionalität in Identifikation und Interventionen."
    },
    "Sokratischer Dialog": {
      "type": "integer",
      "description": "Sokratischer Dialog - Geschickte Frageführung - Förderung der Selbstreflexion - Unterstützung bei eigener Erkenntnisfindung und ist zu bewerten von 1 bis 5: \n\n1 Stern: Sehr schlecht – Keine Förderung von Reflexion oder Erkenntnis.\n2 Sterne: Schlecht – Begrenzte Frageführung und Förderung der Reflexion.\n3 Sterne: Befriedigend – Ausreichende Unterstützung, aber mit Schwächen.\n4 Sterne: Gut – Gute Frageführung und Selbstreflexionsförderung.\n5 Sterne: Ausgezeichnet – Herausragende Unterstützung bei Erkenntnisfindung und Reflexion."
    },
    "begründung": {
      "type": "string",
      "description": "Begründung für die Bewertung"
    }
  }
}

def fit_into_dialoug_schema(id, conversations,label, prior_evaluations=None, evaluation=None,  evaluator=None):

  
  return {
    "id": id,
    "label": label,
    "evaluations": prior_evaluations if prior_evaluations is not None else [] + [

      {
        "evaluator": evaluator,
        "rating": evaluation
      } 
    ] if evaluation is not None else [],
    "conversation": conversations
  }


def send_email(evaluator_name,subject="Evaluation", to_email="mohamed.ahmedel1133@gmail.com",json_text=None,pdf_path=None,text=None):
    # Deine E-Mail-Adresse und Passwort
    from_email = 'Dok-Pro-KI-Report@web.de'
    password = 'Neur0k@rd#2024#'

    # E-Mail-Server und Port
    smtp_server = 'smtp.web.de'
    port = 587

    # E-Mail-Nachricht erstellen
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject+" by "+evaluator_name

    # Textinhalt der E-Mail
    body = f"Evaluation by {evaluator_name}"
    msg.attach(MIMEText(body, 'plain'))
    if json_text:
        # JSON-Text als .json-Datei anhängen
        json_filename = f"evaluation_data_{evaluator_name}.json"
        with open(json_filename, "w") as f:
            json.dump(json_text, f)
        with open(json_filename, "rb") as f:
            attach = MIMEApplication(f.read(),_subtype="json")
        attach.add_header('Content-Disposition','attachment',filename=str(json_filename))
        msg.attach(attach)

    if pdf_path:
        # PDF-Datei anhängen
        pdf_filename = pdf_path
        with open(pdf_filename, "rb") as f:
            attach = MIMEApplication(f.read(),_subtype="pdf")
        attach.add_header('Content-Disposition','attachment',filename=str(pdf_filename))
        msg.attach(attach)
    if text:
        # Textinhalt der E-Mail
        body = text
        msg.attach(MIMEText(body, 'plain'))

    # Verbindung zum SMTP-Server herstellen und E-Mail senden
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
        print("E-Mail gesendet!")
    except Exception as e:
        print(f"Fehler: {e}")
    finally:
        server.quit()