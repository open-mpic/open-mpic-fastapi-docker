from pydantic import BaseModel, Field


class PerspectiveEndpointInfo(BaseModel):
    url: str
    headers: dict[str, str] | None = Field(default_factory=dict)


class PerspectiveEndpoints(BaseModel):
    dcv_endpoint_info: PerspectiveEndpointInfo
    caa_endpoint_info: PerspectiveEndpointInfo
