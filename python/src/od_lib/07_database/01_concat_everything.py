import od_lib.definitions.path_definitions as path_definitions
import xml.etree.ElementTree as et
import pandas as pd
import regex
import time
import datetime
import sys

# input directory
RAW_XML = path_definitions.RAW_XML
SPEECH_CONTENT_INPUT = path_definitions.SPEECH_CONTENT_STAGE_04
SPEECH_CONTENT_INPUT_2 = path_definitions.ELECTORAL_TERM_19_20_STAGE_03 / "electoral_term_19"
SPEECH_CONTENT_INPUT_3 = path_definitions.ELECTORAL_TERM_19_20_STAGE_03 / "electoral_term_20"
CONTRIBUTIONS_EXTENDED_INPUT = path_definitions.CONTRIBUTIONS_EXTENDED_STAGE_03

# output directory
SPEECH_CONTENT_OUTPUT = path_definitions.FINAL
CONTRIBUTIONS_EXTENDED_OUTPUT = path_definitions.FINAL

SPEECH_CONTENT_OUTPUT.mkdir(parents=True, exist_ok=True)
CONTRIBUTIONS_EXTENDED_OUTPUT.mkdir(parents=True, exist_ok=True)

# spoken content

# Placeholder for concating speeches DF of all sessions.
speech_content_01_18 = []


# Walk over all legislature periods.
for folder_path in sorted(SPEECH_CONTENT_INPUT.iterdir()):
    if not folder_path.is_dir():
        continue

    for speech_content_file_path in sorted(folder_path.glob("*.pkl")):
        speech_content_01_18.append(pd.read_pickle(speech_content_file_path))

speech_content_01_18 = pd.concat(speech_content_01_18, sort=False)

speech_content_01_18 = speech_content_01_18.loc[
    :,
    [
        "speech_id",
        "session",
        "first_name",
        "last_name",
        "faction_id",
        "position_short",
        "position_long",
        "politician_id",
        "speech_content",
    ],
]

speech_content_01_18 = speech_content_01_18.rename(columns={"speech_id": "id"})


speech_content_01_18["first_name"] = speech_content_01_18["first_name"].apply(" ".join)

speech_content_01_18["id"] = list(range(len(speech_content_01_18)))

speech_content_01_18["session"] = speech_content_01_18["session"].str.replace(
    r"\.pkl", "", regex=True
)


meta_data = {}

# Open every xml plenar file in every legislature period.
for folder_path in sorted(RAW_XML.iterdir()):
    # Skip e.g. the .DS_Store file.
    if not folder_path.is_dir():
        continue
    term_number = regex.search(r"(?<=electoral_term_)\d{2}", folder_path.stem)
    if term_number is None:
        continue
    term_number = int(term_number.group(0))

    if len(sys.argv) > 1:
        if str(term_number) not in sys.argv:
            continue

    for xml_plenar_file_path in sorted(folder_path.glob("*.xml")):
        tree = et.parse(xml_plenar_file_path)
        # Get the document number, the date of the session and the content.
        # meta_data["document_number"].append(tree.find("NR").text)
        # meta_data["date"].append(tree.find("DATUM").text)
        # document_number = tree.find("NR").text
        date = time.mktime(
            datetime.datetime.strptime(
                tree.find("DATUM").text, "%d.%m.%Y"
            ).timetuple()
        )
        document_number = xml_plenar_file_path.stem
        document_number = int(document_number)
        meta_data[document_number] = date

speech_content_01_18.insert(1, "electoral_term", -1)
speech_content_01_18.insert(4, "document_url", "")
speech_content_01_18["electoral_term"] = speech_content_01_18["session"].apply(
    lambda x: str(x)[:2]
)
speech_content_01_18["session"] = speech_content_01_18["session"].astype("int32")
speech_content_01_18["date"] = speech_content_01_18["session"].apply(meta_data.get)
speech_content_01_18["session"] = speech_content_01_18["session"].apply(
    lambda x: str(x)[-3:]
)

speech_content_01_18["document_url"] = speech_content_01_18.apply(
    lambda row: "https://dip21.bundestag.de/dip21/btp/{0}/{0}{1}.pdf".format(
        row["electoral_term"], row["session"]
    ),
    axis=1,
)

speech_content_01_18["session"] = speech_content_01_18["session"].astype("int32")
speech_content_01_18["electoral_term"] = speech_content_01_18["electoral_term"].astype(
    "int32"
)

speech_content_19 = pd.read_pickle(
    SPEECH_CONTENT_INPUT_2 / "speech_content" / "speech_content.pkl"
)
speech_content_20 = pd.read_pickle(
    SPEECH_CONTENT_INPUT_3 / "speech_content" / "speech_content.pkl"
)

speech_content_19 = speech_content_19.loc[
    :,
    [
        "id",
        "session",
        "first_name",
        "last_name",
        "faction_id",
        "position_short",
        "position_long",
        "politician_id",
        "speech_content",
        "date",
    ],
]
speech_content_20 = speech_content_20.loc[
    :,
    [
        "id",
        "session",
        "first_name",
        "last_name",
        "faction_id",
        "position_short",
        "position_long",
        "politician_id",
        "speech_content",
        "date",
    ],
]


speech_content_19.insert(1, "electoral_term", -1)
speech_content_20.insert(1, "electoral_term", -1)

speech_content_19["electoral_term"] = speech_content_19["session"].apply(
    lambda x: str(x)[:2]
)
speech_content_20["electoral_term"] = speech_content_20["session"].apply(
    lambda x: str(x)[:2]
)
speech_content_19["session"] = speech_content_19["session"].apply(lambda x: str(x)[-3:])
speech_content_20["session"] = speech_content_20["session"].apply(lambda x: str(x)[-3:])

speech_content_19["document_url"] = speech_content_19.apply(
    lambda row: "https://dip21.bundestag.de/dip21/btp/{0}/{0}{1}.pdf".format(
        row["electoral_term"], row["session"]
    ),
    axis=1,
)
speech_content_20["document_url"] = speech_content_20.apply(
    lambda row: "https://dip21.bundestag.de/dip21/btp/{0}/{0}{1}.pdf".format(
        row["electoral_term"], row["session"]
    ),
    axis=1,
)

speech_content_19["electoral_term"] = speech_content_19["electoral_term"].astype(
    "int32"
)
speech_content_20["electoral_term"] = speech_content_20["electoral_term"].astype(
    "int32"
)
speech_content_19["session"] = speech_content_19["session"].astype("int32")
speech_content_20["session"] = speech_content_20["session"].astype("int32")

speech_content = pd.concat([speech_content_01_18, speech_content_19, speech_content_20])

# save data.

speech_content.to_pickle(SPEECH_CONTENT_OUTPUT / "speech_content.pkl")

# Placeholder for concating contributions_extended DF of all sessions.
contributions_extended = []

# Walk over all legislature periods. ___________________________________________
for folder_path in sorted(CONTRIBUTIONS_EXTENDED_INPUT.iterdir()):
    # Skip e.g. the .DS_Store file.
    if not folder_path.is_dir():
        continue
    term_number = regex.search(r"(?<=electoral_term_)\d{2}", folder_path.stem)
    if term_number is None:
        continue
    term_number = int(term_number.group(0))

    for contrib_ext_file_path in sorted(folder_path.glob("*.pkl")):
        contributions_extended.append(pd.read_pickle(contrib_ext_file_path))

contributions_extended = pd.concat(contributions_extended, sort=False)

contributions_extended = contributions_extended.loc[
    :,
    [
        "type",
        "first_name",
        "last_name",
        "faction_id",
        "id",
        "text_position",
        "politician_id",
        "content",
    ],
]

contributions_extended = contributions_extended.rename(
    columns={"id": "speech_id", "politician_id": "politician_id"}
)

contributions_extended.insert(
    0, "id", list(range(len(contributions_extended)))
)

contributions_extended.first_name = (
    contributions_extended.first_name.apply(" ".join)
)

contributions_extended = contributions_extended.astype(
    {
        "id": "int64",
        "type": "object",
        "first_name": "object",
        "last_name": "object",
        "faction_id": "int32",
        "speech_id": "int32",
        "text_position": "int32",
        "politician_id": "int32",
        "content": "object",
    }
)

contributions_extended.to_pickle(
    CONTRIBUTIONS_EXTENDED_OUTPUT / "contributions_extended.pkl"
)
