from lineapy.utils import CaseNotHandledError
from lineapy.data.types import Artifact, CallNode, DataAssetType, NodeValue


def jsonify_node_value(node: NodeValue) -> str:
    """
    These are the post processing steps from the DB artifacts
      for the routes
    """

    if node.value_type in [DataAssetType.Number, DataAssetType.Str]:
        return str(node.value)
    if node.value_type is DataAssetType.PandasDataFrame:
        return node.value.to_csv(index=False)
    raise CaseNotHandledError(
        f"Was not able to jsonify value of type {type(node.value)}"
    )


def jsonify_and_package_artifact(
    self, artifact: Artifact, code: str, call_nodes: CallNode
) -> Dict:
    """
    Again, post processing steps once all the database values are gathered
    """
    json_artifact = artifact.dict()

    # FIXME: done because of API naming discrepency, we should refactor
    #        linea-server so we don't have to do this remapping
    json_artifact["type"] = json_artifact["value_type"]
    del json_artifact["value_type"]

    # FIXME: same as above
    #        done because of API naming discrepency, we should refactor
    #        linea-server so we don't have to do this remapping
    json_artifact["date"] = json_artifact["date_created"]
    del json_artifact["date_created"]

    json_artifact["file"] = ""

    # All the code/token logic needs to be refactored with the new PR

    # json_artifact["code"] = code.dict()

    # token_associations = (
    #     self.session.query(code_token_association_table)
    #     .filter(code_token_association_table.c.code == code.id)
    #     .all()
    # )
    # NOTE/TODO: currently only supports DataFrames and values as tokens
    tokens_json = []
    if token_associations is not None:
        for association in token_associations:
            token_orm = (
                self.session.query(TokenORM)
                .filter(TokenORM.id == association.token)
                .first()
            )
            token_json = Token.from_orm(token_orm).dict()

            # FIXME: we need to check for None here
            intermediate_result = (
                self.session.query(NodeValueORM)
                .filter(NodeValueORM.node_id == token_json["intermediate"])
                .first()
            )
            if intermediate_result is None:
                raise NullValueError("")

            # FIXME: not sure why there is the type error here....
            intermediate_value = jsonify_value(
                intermediate_result.value, intermediate_result.value_type
            )
            intermediate = {
                "file": "",
                "id": token_json["intermediate"],
                "name": "",
                "type": DATASET_TYPE,
                "date": 1372944000,
                "text": intermediate_value,
            }
            token_json["intermediate"] = intermediate
            tokens_json.append(token_json)

    json_artifact["code"]["tokens"] = tokens_json

    return json_artifact
