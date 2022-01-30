import sys
import time

from proxmoxer import ProxmoxAPI

if sys.version_info[0] >= 3:
    # prefer using monoatomic time if available
    def get_time():
        return time.monotonic()


else:

    def get_time():
        return time.time()


class Tasks:
    """Ease-of-use tools for interacting with the tasks endpoints
    in the Proxmox API.
    """

    def __init__(self, proxmox_api: ProxmoxAPI, polling_interval=0.01):
        """Initialize Tasks object

        :param proxmox_api: [description]
        :type proxmox_api: ProxmoxAPI
        :param polling_interval: delay (in seconds) between checking for updates, defaults to 0.01 seconds (100 ms)
        :type polling_interval: float, optional
        """
        self._prox = proxmox_api
        self._polling_interval: int = polling_interval

    def blocking_status(self, task_id: str, timeout: int = 300):
        """Turns getting the status of a Proxmox task into a blocking call
        by polling the API until the task completes

        :param task_id: the UPID of the task
        :type task_id: str
        :param timeout: if the task does not complete in this time (in seconds) return None, defaults to 300
        :type timeout: int, optional
        :return: the status of the task
        :rtype: dict or None
        """

        node = self.decode_upid(task_id)["node"]
        start_time = get_time()
        data = {"status": ""}
        while data["status"] != "stopped":
            data = self._prox.nodes(node).tasks(task_id).status.get()
            if start_time + timeout <= get_time():
                data = None
                break

            time.sleep(self._polling_interval)
        return data

    @staticmethod
    def decode_upid(upid: str):
        """Decodes the sections of a UPID into separate fields

        :return: a Proxmox UPID
        :rtype: dict
        """
        segments = upid.split(":")
        data = {}

        data["node"] = segments[1]
        data["pid"] = int(segments[2], 16)
        data["pstart"] = int(segments[3], 16)
        data["starttime"] = int(segments[4], 16)
        data["type"] = segments[5]
        data["id"] = segments[6]
        data["user"] = segments[7].split("!")[0]
        return data

    @staticmethod
    def decode_log(log_list):
        """Takes in a task's log data and returns a multiline string representation

        :param log_list: The log formatting returned by the Proxmox API
        :type log_list: list of dicts
        :return: a multiline string of the log
        :rtype: str
        """
        str_list = [""] * len(log_list)
        for line in log_list:
            str_list[line["n"] - 1] = line.get("t")

        return "\n".join(str_list)
