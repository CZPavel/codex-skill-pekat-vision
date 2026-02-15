"""Smoke test pro šablonu Code modulu.

Spustitelné mimo PEKAT:
python -m tests.test_code_module_smoke

Cíl: odhalit syntaktické chyby a nejčastější KeyError/IndexError.
"""

import numpy as np

from scripts.code_module_template import main


def test_template_runs_without_errors():
    # Minimal context podobný tomu, co ukazuje KB 3.19
    context = {
        "image": np.zeros((100, 100, 3), dtype=np.uint8),
        "detectedRectangles": [
            {
                "x": 10,
                "y": 10,
                "width": 50,
                "height": 40,
                "classNames": [{"label": "My Rectangle"}],
            }
        ],
        "result": True,
    }

    main(context, module_item={"dummy": 1})

    assert isinstance(context["image"], np.ndarray)
    assert context["image"].shape[0] > 0 and context["image"].shape[1] > 0


if __name__ == "__main__":
    test_template_runs_without_errors()
    print("OK")
