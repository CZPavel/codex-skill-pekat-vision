from code_module_template import main


class FakeImage:
    shape = (100, 120, 3)

    def __getitem__(self, _key):
        return self

    def copy(self):
        return FakeImage()


def rectangle(label="part"):
    return {"x": 10, "y": 20, "width": 30, "height": 40, "classNames": [{"label": label}]}


def test_form_entrypoint_crops_without_changing_result():
    context = {"image": FakeImage(), "detectedRectangles": [rectangle()], "result": True}
    main(context, {"target_label": "part", "crop_enabled": True})
    assert isinstance(context["image"], FakeImage)
    assert context["code_template_status"] == "cropped"
    assert context["result"] is True


def test_missing_inputs_are_diagnostic_only():
    context = {"result": False}
    main(context)
    assert context == {"result": False, "code_template_status": "rectangle_not_found"}
