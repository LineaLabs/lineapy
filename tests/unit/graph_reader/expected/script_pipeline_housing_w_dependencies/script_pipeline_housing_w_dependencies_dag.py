from script_pipeline_housing_w_dependencies_module import (
    get_assets_for_artifact_y_and_downstream,
    get_pvalue,
    get_y,
)


def pipeline():
    assets = get_assets_for_artifact_y_and_downstream()
    y = get_y(assets)
    p = get_pvalue(assets, y)
    return y, p


if __name__ == "__main__":
    pipeline()
