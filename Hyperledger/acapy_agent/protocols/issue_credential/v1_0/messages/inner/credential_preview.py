"""A credential preview inner object."""

from typing import Optional, Sequence

from marshmallow import EXCLUDE, fields

from ......messaging.models.base import BaseModel, BaseModelSchema
from ......wallet.util import b64_to_str
from .....didcomm_prefix import DIDCommPrefix
from ...message_types import CREDENTIAL_PREVIEW


class CredAttrSpec(BaseModel):
    """Class representing a preview of an attibute."""

    class Meta:
        """Attribute preview metadata."""

        schema_class = "CredAttrSpecSchema"

    def __init__(
        self, *, name: str, value: str, mime_type: Optional[str] = None, **kwargs
    ):
        """Initialize attribute preview object.

        Args:
            name: attribute name
            value: attribute value; caller must base64-encode for attributes with
                non-empty MIME type
            mime_type: MIME type (default null)
            kwargs: additional keyword arguments to map into message class properties

        """
        super().__init__(**kwargs)

        self.name = name
        self.value = value
        self.mime_type = mime_type.lower() if mime_type else None

    @staticmethod
    def list_plain(plain: dict):
        """Return a list of `CredAttrSpec` without MIME types from names/values.

        Args:
            plain: dict mapping names to values

        Returns:
            List of CredAttrSpecs with no MIME types

        """
        return [CredAttrSpec(name=k, value=plain[k]) for k in plain]

    def b64_decoded_value(self) -> str:
        """Value, base64-decoded if applicable."""

        return b64_to_str(self.value) if self.value and self.mime_type else self.value

    def __eq__(self, other):
        """Equality comparator."""

        if self.name != other.name:
            return False  # distinct attribute names

        if self.mime_type != other.mime_type:
            return False  # distinct MIME types

        return self.b64_decoded_value() == other.b64_decoded_value()


class CredAttrSpecSchema(BaseModelSchema):
    """Attribute preview schema."""

    class Meta:
        """Attribute preview schema metadata."""

        model_class = CredAttrSpec
        unknown = EXCLUDE

    name = fields.Str(
        required=True,
        metadata={"description": "Attribute name", "example": "favourite_drink"},
    )
    mime_type = fields.Str(
        required=False,
        data_key="mime-type",
        allow_none=True,
        metadata={
            "description": "MIME type: omit for (null) default",
            "example": "image/jpeg",
        },
    )
    value = fields.Str(
        required=True,
        metadata={
            "description": "Attribute value: base64-encode if MIME type is present",
            "example": "martini",
        },
    )


class CredentialPreview(BaseModel):
    """Class representing a credential preview inner object."""

    class Meta:
        """Credential preview metadata."""

        schema_class = "CredentialPreviewSchema"
        message_type = CREDENTIAL_PREVIEW

    def __init__(
        self,
        *,
        _type: Optional[str] = None,
        attributes: Sequence[CredAttrSpec] = None,
        **kwargs,
    ):
        """Initialize credential preview object.

        Args:
            _type: formalism for Marshmallow model creation: ignored
            attributes (list): list of attribute preview dicts; e.g., [
                {
                    "name": "attribute_name",
                    "value": "value"
                },
                {
                    "name": "icon",
                    "mime-type": "image/png",
                    "value": "cG90YXRv"
                }
            ]
            kwargs: additional keyword arguments to map into message class properties

        """
        super().__init__(**kwargs)
        self.attributes = list(attributes) if attributes else []

    @property
    def _type(self):
        """Accessor for message type."""
        return DIDCommPrefix.qualify_current(CredentialPreview.Meta.message_type)

    def attr_dict(self, decode: bool = False):
        """Return name:value pair per attribute.

        Args:
            decode: whether first to decode attributes with MIME type

        """

        return {
            attr.name: (
                b64_to_str(attr.value) if attr.mime_type and decode else attr.value
            )
            for attr in self.attributes
        }

    def mime_types(self):
        """Return per-attribute mapping from name to MIME type.

        Return empty dict if no attribute has MIME type.

        """
        return {attr.name: attr.mime_type for attr in self.attributes if attr.mime_type}


class CredentialPreviewSchema(BaseModelSchema):
    """Credential preview schema."""

    class Meta:
        """Credential preview schema metadata."""

        model_class = CredentialPreview
        unknown = EXCLUDE

    _type = fields.Str(
        required=False,
        data_key="@type",
        metadata={
            "description": "Message type identifier",
            "example": CREDENTIAL_PREVIEW,
        },
    )
    attributes = fields.Nested(
        CredAttrSpecSchema, many=True, required=True, data_key="attributes"
    )
