import os
import re
import logging
import warnings
from typing import Any, Dict, Optional, Text, List, Union
from rasa.nlu.config import RasaNLUModelConfig
from rasa.nlu.extractors.extractor import EntityExtractor
from rasa.nlu.model import Metadata
from rasa.nlu.training_data import Message, TrainingData
from rasa.nlu.utils import write_json_to_file
import rasa.utils.common as common_utils
import rasa.utils.io
from rasa.constants import DOCS_URL_TRAINING_DATA_NLU

logger = logging.getLogger(__name__)


class RegexEntityExtractor(EntityExtractor):
    # This extractor may be kind of extreme as it takes user's message
    # and return regex match.
    # Confidence will be 1.0 just like Duckling
    # provides = ["entities"]

    def __init__(
        self,
        component_config: Optional[Dict[Text, Any]] = None,
        regex_features: Optional[List[Dict[Text, Text]]] = None,
        lookup_tables: Optional[List[Dict[Text, Union[Text, List]]]] = None,
    ) -> None:
        super(RegexEntityExtractor, self).__init__(component_config)
        self.regex_feature = regex_features if regex_features else []
        lookup_tables = lookup_tables or []
        self._add_lookup_table_regexes(lookup_tables)

    def train(
        self,
        training_data: TrainingData,
        config: Optional[RasaNLUModelConfig] = None,
        **kwargs: Any,
    ) -> None:
        self.regex_feature = training_data.regex_features
        self._add_lookup_table_regexes(training_data.lookup_tables)
        # logger.info(self.regex_feature)

    def match_regex(self, message):
        extracted = []
        for d in self.regex_feature:
            for match in re.finditer(pattern=d["pattern"], string=message):
                span = match.span()
                if match:
                    entity = {
                        "start": span[0],
                        "end": span[1],
                        "value": match.group(),
                        "confidence": 1.0,
                        "entity": d["name"],
                    }
                    if entity not in extracted:
                        extracted.append(entity)
        # print(extracted)
        extracted = self.add_extractor_name(extracted)
        return extracted

    def process(self, message: Message, **kwargs: Any) -> None:
        """Process an incoming message."""
        extracted = self.match_regex(message.text)
        message.set(
            "entities", message.get("entities", []) + extracted, add_to_output=True
        )

    def _generate_lookup_regex(
        self, lookup_table: Dict[Text, Union[Text, List[Text]]]
    ) -> Text:
        """creates a regex out of the contents of a lookup table file"""
        lookup_elements = lookup_table["elements"]
        elements_to_regex = []

        # if it's a list, it should be the elements directly
        if isinstance(lookup_elements, list):
            elements_to_regex = lookup_elements
            common_utils.raise_warning(
                "Directly including lookup tables as a list is deprecated since Rasa "
                "1.6.",
                FutureWarning,
                docs=DOCS_URL_TRAINING_DATA_NLU + "#lookup-tables",
            )

        # otherwise it's a file path.
        else:

            try:
                f = open(lookup_elements, "r", encoding=rasa.utils.io.DEFAULT_ENCODING)
            except OSError:
                raise ValueError(
                    f"Could not load lookup table {lookup_elements}. "
                    f"Please make sure you've provided the correct path."
                )

            with f:
                for line in f:
                    new_element = line.strip()
                    if new_element:
                        elements_to_regex.append(new_element)

        # sanitize the regex, escape special characters
        elements_sanitized = [re.escape(e) for e in elements_to_regex]

        # regex matching elements with word boundaries on either side
        regex_string = "(?i)(\\b" + "\\b|\\b".join(elements_sanitized) + "\\b)"
        return regex_string

    def _add_lookup_table_regexes(
        self, lookup_tables: List[Dict[Text, Union[Text, List]]]
    ) -> None:
        """appends the regex features from the lookup tables to self.regex_feature"""
        for table in lookup_tables:
            regex_pattern = self._generate_lookup_regex(table)
            lookup_regex = {"name": table["name"], "pattern": regex_pattern}
            self.regex_feature.append(lookup_regex)

    @classmethod
    def load(
        cls,
        meta: Dict[Text, Any],
        model_dir: Optional[Text] = None,
        model_metadata: Optional[Metadata] = None,
        cached_component: Optional["RegexEntityExtractor"] = None,
        **kwargs: Any,
    ) -> "RegexEntityExtractor":
        file_name = meta.get("file")
        if not file_name:
            regex_features = None
            return cls(meta, regex_features)
        # w/o string cast, mypy will tell me
        # expected "Union[str, _PathLike[str]]"
        regex_pattern_file = os.path.join(str(model_dir), file_name)
        if os.path.isfile(regex_pattern_file):
            regex_features = rasa.utils.io.read_json_file(regex_pattern_file)
        else:
            regex_features = None
            warnings.warn(
                "Failed to load regex pattern file from '{}'".format(regex_pattern_file)
            )
        return cls(meta, regex_features)

    def persist(self, file_name: Text, model_dir: Text) -> Optional[Dict[Text, Any]]:
        """Persist this component to disk for future loading."""
        if self.regex_feature:
            file_name = file_name + ".json"
            regex_feature_file = os.path.join(model_dir, file_name)
            write_json_to_file(
                regex_feature_file, self.regex_feature, separators=(",", ": ")
            )
            return {"file": file_name}
        else:
            return {"file": None}
