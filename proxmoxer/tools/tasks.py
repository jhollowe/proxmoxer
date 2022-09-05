import sys
import time
from typing import List, Union

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from proxmoxer.core import ProxmoxAPI


class UpidData(TypedDict):
    """
    Type of a decoded UPID
    """

    upid: str
    node: str
    pid: int
    pstart: int
    starttime: int
    type: str
    id: str
    user: str
    comment: str


class LogLine(TypedDict):
    """
    The format of a line of a log returned by prox.nodes.{node}.tasks.{upid}.log.get()
    """

    n: int
    t: str


class Tasks:
    """
    Ease-of-use tools for interacting with the tasks endpoints
    in the Proxmox API.
    """

    @staticmethod
    def blocking_status(
        prox: ProxmoxAPI, task_id: str, timeout: int = 300, polling_interval: float = 0.01
    ) -> Union[dict, None]:
        """
        Turns getting the status of a Proxmox task into a blocking call
        by polling the API until the task completes

        :param prox: The Proxmox object used to query for status
        :type prox: ProxmoxAPI
        :param task_id: the UPID of the task
        :type task_id: str
        :param timeout: If the task does not complete in this time (in seconds) return None, defaults to 300
        :type timeout: int, optional
        :param polling_interval: _description_, defaults to 0.01
        :type polling_interval: float, optional
        :return: the status of the task
        :rtype: dict
        """
        node: str = Tasks.decode_upid(task_id)["node"]
        start_time: float = time.monotonic()
        data = {"status": ""}
        while data["status"] != "stopped":
            data = prox.nodes(node).tasks(task_id).status.get()
            if start_time + timeout <= time.monotonic():
                data = None  # type: ignore
                break

            time.sleep(polling_interval)
        return data

    @staticmethod
    def decode_upid(upid: str) -> UpidData:
        """
        Decodes the sections of a UPID into separate fields

        :param upid: a UPID string
        :type upid: str
        :return: The decoded information from the UPID
        :rtype: dict
        """
        segments: List[str] = upid.split(":")
        if segments[0] != "UPID" or len(segments) != 9:
            raise AssertionError("UPID is not in the correct format")

        data: UpidData = {
            "upid": upid,
            "node": segments[1],
            "pid": int(segments[2], 16),
            "pstart": int(segments[3], 16),
            "starttime": int(segments[4], 16),
            "type": segments[5],
            "id": segments[6],
            "user": segments[7].split("!")[0],
            "comment": segments[8],
        }
        return data

    @staticmethod
    def decode_log(log_list: List[LogLine]) -> str:
        """
        Takes in a task's log data and returns a multiline string representation

        :param log_list: The log formatting returned by the Proxmox API
        :type log_list: list of dicts
        :return: a multiline string of the log
        :rtype: str
        """
        str_list = [""] * len(log_list)
        for line in log_list:
            str_list[line["n"] - 1] = line.get("t", "")

        return "\n".join(str_list)
