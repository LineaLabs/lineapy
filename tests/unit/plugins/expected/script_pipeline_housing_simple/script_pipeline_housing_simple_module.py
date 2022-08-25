import pandas as pd
from sklearn.ensemble import RandomForestClassifier


def get_pvalue():
    assets = pd.read_csv(
        "https://raw.githubusercontent.com/LineaLabs/lineapy/main/tests/ames_train_cleaned.csv"
    )

    def is_new(col):
        return col > 1970

    assets["is_new"] = is_new(assets["Year_Built"])
    clf = RandomForestClassifier(random_state=0)
    y = assets["is_new"]
    x = assets[["SalePrice", "Lot_Area", "Garage_Area"]]
    clf.fit(x, y)
    p = clf.predict([[100 * 1000, 10, 4]])
    return p


def run_session_including_pvalue():
    # Given multiple artifacts, we need to save each right after
    # its calculation to protect from any irrelevant downstream
    # mutations (e.g., inside other artifact calculations)
    import copy

    artifacts = dict()
    p = get_pvalue()
    artifacts["p value"] = copy.deepcopy(p)
    return artifacts


def run_all_sessions():
    artifacts = dict()
    artifacts.update(run_session_including_pvalue())
    return artifacts


if __name__ == "__main__":
    run_all_sessions()
