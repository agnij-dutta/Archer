import unittest

from features.config import FFMPEG_INPUT_ARGS_DEFAULT, ArcherConfig
from features.ffmpeg_presets import parse_preset_input


class TestFfmpegPresets(unittest.TestCase):
    def setUp(self):
        self.default_ffmpeg = {
            "mqtt": {"host": "mqtt"},
            "cameras": {
                "back": {
                    "ffmpeg": {
                        "inputs": [
                            {
                                "path": "rtsp://10.0.0.1:554/video",
                                "roles": ["detect", "rtmp"],
                            }
                        ],
                        "output_args": {
                            "detect": "-f rawvideo -pix_fmt yuv420p",
                            "record": "-f segment -segment_time 10 -segment_format mp4 -reset_timestamps 1 -strftime 1 -c copy -an",
                            "rtmp": "-c copy -f flv",
                        },
                    },
                    "detect": {
                        "height": 1080,
                        "width": 1920,
                        "fps": 5,
                    },
                    "record": {
                        "enabled": True,
                    },
                    "rtmp": {
                        "enabled": True,
                    },
                    "name": "back",
                }
            },
        }

    def test_default_ffmpeg(self):
        Archer_config = ArcherConfig(**self.default_ffmpeg)
        Archer_config.cameras["back"].create_ffmpeg_cmds()
        assert self.default_ffmpeg == Archer_config.dict(exclude_unset=True)

    def test_ffmpeg_hwaccel_preset(self):
        self.default_ffmpeg["cameras"]["back"]["ffmpeg"][
            "hwaccel_args"
        ] = "preset-rpi-64-h264"
        Archer_config = ArcherConfig(**self.default_ffmpeg)
        Archer_config.cameras["back"].create_ffmpeg_cmds()
        assert "preset-rpi-64-h264" not in (
            " ".join(Archer_config.cameras["back"].ffmpeg_cmds[0]["cmd"])
        )
        assert "-c:v:1 h264_v4l2m2m" in (
            " ".join(Archer_config.cameras["back"].ffmpeg_cmds[0]["cmd"])
        )

    def test_ffmpeg_hwaccel_not_preset(self):
        self.default_ffmpeg["cameras"]["back"]["ffmpeg"][
            "hwaccel_args"
        ] = "-other-hwaccel args"
        Archer_config = ArcherConfig(**self.default_ffmpeg)
        Archer_config.cameras["back"].create_ffmpeg_cmds()
        assert "-other-hwaccel args" in (
            " ".join(Archer_config.cameras["back"].ffmpeg_cmds[0]["cmd"])
        )

    def test_ffmpeg_hwaccel_scale_preset(self):
        self.default_ffmpeg["cameras"]["back"]["ffmpeg"][
            "hwaccel_args"
        ] = "preset-nvidia-h264"
        self.default_ffmpeg["cameras"]["back"]["detect"] = {
            "height": 1920,
            "width": 2560,
            "fps": 10,
        }
        Archer_config = ArcherConfig(**self.default_ffmpeg)
        Archer_config.cameras["back"].create_ffmpeg_cmds()
        assert "preset-nvidia-h264" not in (
            " ".join(Archer_config.cameras["back"].ffmpeg_cmds[0]["cmd"])
        )
        assert (
            "fps=10,scale_cuda=w=2560:h=1920:format=nv12,hwdownload,format=nv12,format=yuv420p"
            in (" ".join(Archer_config.cameras["back"].ffmpeg_cmds[0]["cmd"]))
        )

    def test_default_ffmpeg_input_arg_preset(self):
        Archer_config = ArcherConfig(**self.default_ffmpeg)

        self.default_ffmpeg["cameras"]["back"]["ffmpeg"][
            "input_args"
        ] = "preset-rtsp-generic"
        Archer_preset_config = ArcherConfig(**self.default_ffmpeg)
        Archer_config.cameras["back"].create_ffmpeg_cmds()
        Archer_preset_config.cameras["back"].create_ffmpeg_cmds()
        assert (
            # Ignore global and user_agent args in comparison
            Archer_preset_config.cameras["back"].ffmpeg_cmds[0]["cmd"]
            == Archer_config.cameras["back"].ffmpeg_cmds[0]["cmd"]
        )

    def test_ffmpeg_input_preset(self):
        self.default_ffmpeg["cameras"]["back"]["ffmpeg"][
            "input_args"
        ] = "preset-rtmp-generic"
        Archer_config = ArcherConfig(**self.default_ffmpeg)
        Archer_config.cameras["back"].create_ffmpeg_cmds()
        assert "preset-rtmp-generic" not in (
            " ".join(Archer_config.cameras["back"].ffmpeg_cmds[0]["cmd"])
        )
        assert (" ".join(parse_preset_input("preset-rtmp-generic", 5))) in (
            " ".join(Archer_config.cameras["back"].ffmpeg_cmds[0]["cmd"])
        )

    def test_ffmpeg_input_args_as_string(self):
        # Strip user_agent args here to avoid handling quoting issues
        defaultArgsList = parse_preset_input(FFMPEG_INPUT_ARGS_DEFAULT, 5)[2::]
        argsString = " ".join(defaultArgsList) + ' -some "arg with space"'
        argsList = defaultArgsList + ["-some", "arg with space"]
        self.default_ffmpeg["cameras"]["back"]["ffmpeg"]["input_args"] = argsString
        Archer_config = ArcherConfig(**self.default_ffmpeg)
        Archer_config.cameras["back"].create_ffmpeg_cmds()
        assert set(argsList).issubset(
            Archer_config.cameras["back"].ffmpeg_cmds[0]["cmd"]
        )

    def test_ffmpeg_input_not_preset(self):
        self.default_ffmpeg["cameras"]["back"]["ffmpeg"]["input_args"] = "-some inputs"
        Archer_config = ArcherConfig(**self.default_ffmpeg)
        Archer_config.cameras["back"].create_ffmpeg_cmds()
        assert "-some inputs" in (
            " ".join(Archer_config.cameras["back"].ffmpeg_cmds[0]["cmd"])
        )

    def test_ffmpeg_output_record_preset(self):
        self.default_ffmpeg["cameras"]["back"]["ffmpeg"]["output_args"][
            "record"
        ] = "preset-record-generic-audio-aac"
        Archer_config = ArcherConfig(**self.default_ffmpeg)
        Archer_config.cameras["back"].create_ffmpeg_cmds()
        assert "preset-record-generic-audio-aac" not in (
            " ".join(Archer_config.cameras["back"].ffmpeg_cmds[0]["cmd"])
        )
        assert "-c:v copy -c:a aac" in (
            " ".join(Archer_config.cameras["back"].ffmpeg_cmds[0]["cmd"])
        )

    def test_ffmpeg_output_record_not_preset(self):
        self.default_ffmpeg["cameras"]["back"]["ffmpeg"]["output_args"][
            "record"
        ] = "-some output"
        Archer_config = ArcherConfig(**self.default_ffmpeg)
        Archer_config.cameras["back"].create_ffmpeg_cmds()
        assert "-some output" in (
            " ".join(Archer_config.cameras["back"].ffmpeg_cmds[0]["cmd"])
        )

    def test_ffmpeg_output_rtmp_preset(self):
        self.default_ffmpeg["cameras"]["back"]["ffmpeg"]["output_args"][
            "rtmp"
        ] = "preset-rtmp-jpeg"
        Archer_config = ArcherConfig(**self.default_ffmpeg)
        Archer_config.cameras["back"].create_ffmpeg_cmds()
        assert "preset-rtmp-jpeg" not in (
            " ".join(Archer_config.cameras["back"].ffmpeg_cmds[0]["cmd"])
        )
        assert "-c:v libx264" in (
            " ".join(Archer_config.cameras["back"].ffmpeg_cmds[0]["cmd"])
        )

    def test_ffmpeg_output_rtmp_not_preset(self):
        self.default_ffmpeg["cameras"]["back"]["ffmpeg"]["output_args"][
            "rtmp"
        ] = "-some output"
        Archer_config = ArcherConfig(**self.default_ffmpeg)
        Archer_config.cameras["back"].create_ffmpeg_cmds()
        assert "-some output" in (
            " ".join(Archer_config.cameras["back"].ffmpeg_cmds[0]["cmd"])
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
