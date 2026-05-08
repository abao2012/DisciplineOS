from disciplineos.web import _browse_path


def test_path_browser_lists_local_directory(tmp_path) -> None:
    tmp_path.joinpath("folder").mkdir()
    tmp_path.joinpath("file.csv").write_text("symbol\nAAA\n", encoding="utf-8")

    result = _browse_path(str(tmp_path))

    names = {item["name"]: item for item in result["entries"]}
    assert result["current_path"] == str(tmp_path)
    assert names["folder"]["is_dir"] is True
    assert names["file.csv"]["is_dir"] is False
