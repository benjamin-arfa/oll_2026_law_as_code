"""Enumerated types used by the Bern scholarship legislation."""

from openfisca_core.indexed_enums import Enum


class Staatsangehoerigkeit(Enum):
    """Citizenship status for scholarship eligibility (Art. 12 Abs. 1 lit. b–d ABG)."""

    schweizer = "Schweizer Bürgerrecht"
    eu_efta_niederlassung = (
        "EU-/EFTA-Bürger oder Personen mit Niederlassungsbewilligung C"
    )
    aufenthaltsbewilligung_b = (
        "Aufenthaltsbewilligung B mit ausreichender Aufenthaltsdauer"
    )
    fluechtling_staatenlos = "Anerkannte Flüchtlinge oder Staatenlose"
    andere = "Andere — keine Anspruchsberechtigung"


class Ausbildungstyp(Enum):
    """Type of training (Art. 6 ABG)."""

    vorbildung = "Vorbildung"
    erstausbildung = "Erstausbildung"
    zweitausbildung = "Zweitausbildung"
    hoehere_berufsbildung = "Höhere Berufsbildung"
    umschulung = "Umschulung"
    primarstufe = "Primarstufe (nicht anerkannt)"
    sekundarstufe_i = "Sekundarstufe I (nicht anerkannt)"
    weiterbildung = "Berufsorientierte Weiterbildung (nicht anerkannt)"
    zweite_hochschulausbildung = "Zweite Hochschulausbildung (nicht anerkannt)"


class Ausbildungsstufe(Enum):
    """Educational level — relevant for the type of grant (Art. 10 ABG)."""

    sekundarstufe_ii = "Sekundarstufe II"
    tertiaerstufe = "Tertiärstufe"
    nicht_anerkannt = "Nicht anerkannte Stufe"


class WohnsitzGrundlage(Enum):
    """How the stipend-relevant residence is established (Art. 13 ABG)."""

    elterlicher_wohnsitz = "Zivilrechtlicher Wohnsitz der Eltern in Bern"
    elternlos = "Elternlos — eigener Wohnsitz in Bern"
    eltern_im_ausland = "Eltern im Ausland — eigener Wohnsitz in Bern"
    fluechtling_staatenlos = "Flüchtling/Staatenlos mit Aufenthalt in Bern"
    finanziell_unabhaengig = (
        "Volljährig, finanziell unabhängig durch eigene Erwerbstätigkeit"
    )
    keiner = "Kein stipendienrechtlicher Wohnsitz im Kanton Bern"
