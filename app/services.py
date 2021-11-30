import os
import subprocess
import sys
import threading

# Not used now, leaving it here for future use with command line tools
class LineSubProcess(object):
    """
    Class to communicate with arbitrary line-based bash scripts.
    Uses various mechanism to enforce line buffering.

    # When calling python scripts ...
        You need to use -u flag, e.g. `python -u my_script.py`
        instead of `python my_script.py` to prevent python interpreter's
        internal buffering.

    """
    # TODO: handle stderr

    # Prefixing a command with this sets up
    # stdout & stderr buffering to line-based:
    prefix = "stdbuf -oL -eL "

    @staticmethod
    def get_process(command):
        stderr = sys.stderr if has_fileno(sys.stderr) else None
        return Popen(
            LineSubProcess.prefix + command,
            shell=True,  # enable entering whole command as a single string
            bufsize=1,  # line buffer
            universal_newlines=True,  # string-based input/output
            stdin=PIPE,
            stdout=PIPE,
            stderr=stderr
        )

    def __init__(self, command):
        """
        ...
        Make sure the given command does not buffer input/output by itself.
        """
        self.command = command
        self.process = LineSubProcess.get_process(self.command)

    def __call__(self, line):

        assert "\n" not in line

        try:
            self.process.stdin.write(line + "\n")
        except ValueError:
            # In the case the process has died for some reason,
            # try to invoke it once again.
            self.process = LineSubProcess.get_process(self.command)
            self.process.stdin.write(line + "\n")

        return self.process.stdout.readline().strip()

    def __del__(self):
        self.process.kill()


def get_joined_json_from_json(data, tool):
    for i in range(len(data["sentences"])):
        print ("%s:%s"%(i,data["sentences"][i]))
        print(data["sentences"][i]["tgt"]['text'])
        #data[i]["src"]["text"]=data[i]["tgt"]["text"]
        data["sentences"][i]["tgt"]["text"]=tool(data["sentences"][i]["tgt"]["text"])
    return data


# Simplified, non-threadsafe version for force_align.py
# Use the version in realtime for development
class Aligner:

    def __init__(self, fwd_params, fwd_err, rev_params, rev_err, heuristic='grow-diag-final-and', build_root="/doc_translation/fast_align/build"):

        fast_align = os.path.join(build_root, 'fast_align')
        atools = os.path.join(build_root, 'atools')

        (fwd_T, fwd_m) = self.read_err(fwd_err)
        (rev_T, rev_m) = self.read_err(rev_err)

        fwd_cmd = [fast_align, '-i', '-', '-d', '-T', fwd_T, '-m', fwd_m, '-f', fwd_params]
        rev_cmd = [fast_align, '-i', '-', '-d', '-T', rev_T, '-m', rev_m, '-f', rev_params, '-r']
        tools_cmd = [atools, '-i', '-', '-j', '-', '-c', heuristic]

        self.fwd_align = popen_io(fwd_cmd)
        self.rev_align = popen_io(rev_cmd)
        self.tools = popen_io(tools_cmd)

    def __call__(self, line):
        self.fwd_align.stdin.write('{}\n'.format(line))
        self.rev_align.stdin.write('{}\n'.format(line))
        # f words ||| e words ||| links ||| score
        fwd_line = self.fwd_align.stdout.readline().split('|||')[2].strip()
        rev_line = self.rev_align.stdout.readline().split('|||')[2].strip()
        self.tools.stdin.write('{}\n'.format(fwd_line))
        self.tools.stdin.write('{}\n'.format(rev_line))
        al_line = self.tools.stdout.readline().strip()
        return al_line

    def close(self):
        self.fwd_align.stdin.close()
        self.fwd_align.wait()
        self.rev_align.stdin.close()
        self.rev_align.wait()
        self.tools.stdin.close()
        self.tools.wait()

    def read_err(self, err):
        (T, m) = ('', '')
        for line in open(err):
            # expected target length = source length * N
            if 'expected target length' in line:
                m = line.split()[-1]
            # final tension: N
            elif 'final tension' in line:
                T = line.split()[-1]
        return (T, m)


def popen_io(cmd):
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, universal_newlines=True)
    def consume(s):
        for _ in s:
            pass
    threading.Thread(target=consume, args=(p.stderr,)).start()
    return p


class AlignerService:
    def __init__(self, iterable=(), **kwargs):
        self.__dict__.update(iterable, **kwargs)
        self.aligner = Aligner(self.fwd_params,self.fwd_err,self.rev_params,self.rev_err)
        print(self.__dict__)

    def do(self, data):
        for i in range(len(data["sentences"])):
            src=data["sentences"][i]["src"]["text"]
            tgt=data["sentences"][i]["tgt"]["text"]
            if src.isspace() or tgt.isspace()  or src=='' or  tgt=='':
                a=''
            else:
                a=self.aligner(' ||| '.join((data["sentences"][i]["src"]["text"], data["sentences"][i]["tgt"]["text"])))
            data["sentences"][i]["alignment"]=a
        return data

