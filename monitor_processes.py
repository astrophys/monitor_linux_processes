# Author : Ali Snedden
# Date   : 04/23/24
# License: MIT
# Notes :
#   Only works on linux
#
#
#
#
#
"""This code does stuff
"""
#import os
import sys
import time
import argparse
import subprocess

class Process:
    """Process from a user"""
    def __init__(self, pid : int, user : str, virt : str, res : str,
                 shr : str, state : str, percentcpu : float, percentmem : float,
                 localtime : str, timesecs : int, command : str):
        """Monitor user processes by using Python

        Args:

        Returns:

        Raises:
        """
        def parse_mem(memstr : str) -> float :
            """Parse memory string from top, handle case when in different units

            Args:
                memstr : (str) string of memory taken from top

            Returns:
                float in GiB

            Raises:
            """
            try :
                if 't' in memstr.lower():
                    mem = memstr.lower().split('t')[0]
                    mem = float(mem) * 1024
                if 'g' in memstr.lower():
                    mem = memstr.lower().split('g')[0]
                    mem = float(mem)
                elif 'm' in memstr.lower():
                    mem = memstr.lower().split('m')[0]
                    mem = float(mem) / 1024
                elif 'k' in memstr.lower():
                    mem = memstr.lower().split('k')[0]
                    mem = float(mem) / (1024**2)
                else :
                    mem = float(memstr) / (1024**2)
                return mem
            except AttributeError :
                if type(memstr) == float:
                    return memstr
        self.pid=pid
        self.user=user
        # In kilobytes by default - keep everything in GiB
        self.virt = parse_mem(virt)
        self.res  = parse_mem(res)
        self.shr  = parse_mem(shr)
        self.state=state
        self.percentcpu=percentcpu
        self.percentmem=percentmem
        self.localtime=localtime
        self.timesecs=timesecs
        self.command=command


    def write(self, fout) -> None :
        """Write out data to a file

        Args:
            fout : (file) open file to write to

        Returns:
            Nothing

        Raises:
        """
        fout.write("{:<18} : {:<8} : {:<9} {:<5} {:<5.6f} {:<5.6f} {:<5.6f} {:<3.2f} "
                   "{:<3.2f} {}\n".format(self.localtime, self.timesecs, self.pid,
                                        self.user, self.virt, self.res, self.shr,
                                        self.percentcpu, self.percentmem,
                                        self.command))


def total_process(procL : list) -> Process :
    """Take list of Process's, sum up their values and returns a 'total' Process

    Args:
        procL : (list) of Process's

    Returns:
        Process

    Raises:
    """
    virt= 0
    res = 0
    shr = 0
    percentcpu = 0
    percentmem = 0
    localtime = procL[0].localtime
    timesecs  = procL[0].timesecs
    for proc in procL:
        if proc.localtime != localtime or proc.timesecs != timesecs :
            raise ValueError("ERROR!! procL aren't all from the same localtime "
                             "or have the same timesecs")
        virt += proc.virt
        res  += proc.res
        shr  += proc.shr
        percentcpu += proc.percentcpu
        percentmem += proc.percentmem
    totproc = Process(pid = -1, user = proc.user, virt = virt, res = res,
                      shr = shr, state = "N/A", percentcpu = percentcpu,
                      percentmem = percentmem, localtime = proc.localtime,
                      timesecs = proc.timesecs, command = "TOTALPROC")
    return totproc


def main():
    """Monitor user processes by using Python

    Args:

    Returns:

    Raises:
    """
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--user', metavar='username', type=str,
                        help='Username')
    parser.add_argument('--delay', metavar='delay', type=int,
                        help='Delay in (integer) seconds between query')
    parser.add_argument('--outstem', metavar='output_path_stem', type=int,
                        help='Output path stem')
    args = parser.parse_args()
    user = args.user
    delay = args.delay
    start = time.time()
    startlocal = time.localtime()
    procL = []
    print("{}-{}-{}T{}:{}:{}".format(startlocal.tm_year, startlocal.tm_mon,
          startlocal.tm_mday,startlocal.tm_hour,startlocal.tm_min,startlocal.tm_sec))
    totfile = open("{}-total.txt".format(args.outstem), "w+")
    totfile.write("{:<18} : {:<8} : {:<9} {:<5} {:<5} {:<5} {:<3} {:<3} "
                  "{}\n".format("Date", "time", "pid", "user", "virt", "res", "shr",
                              "%cpu", "%mem", "command"))
    allfile = open("{}-all.txt".format(args.outstem), "w+")
    allfile.write("{:<18} : {:<8} : {:<9} {:<5} {:<5} {:<5} {:<3} {:<3} "
                  "{}\n".format("Date", "time", "pid", "user", "virt", "res", "shr",
                              "%cpu", "%mem", "command"))

    while True:
        # Should be careful of string injection
        # https://stackoverflow.com/a/28756533/4021436
        string="top -b -u {} -n 1 | grep {}".format(user,user)
        top = subprocess.getoutput(string)
        print(top)
        topL = top.split('\n')
        procsattimeL = []       # procs ONLY at this current time
        # Get time
        localtime = time.localtime()
        localtime = "{}-{}-{}T{}:{}:{}".format(localtime.tm_year,
                    localtime.tm_mon, localtime.tm_mday, localtime.tm_hour,
                    localtime.tm_min, localtime.tm_sec)
        timesecs = time.time() - start
        for line in topL:
            line = line.split()
            proc = Process(pid=int(line[0]), user=line[1], virt=line[4],
                              res=line[5], shr=line[6], state=line[7],
                              percentcpu=float(line[8]), percentmem=float(line[9]),
                              localtime=localtime, timesecs=timesecs,
                              command = line[-1])
            procL.append(proc)
            procsattimeL.append(proc)
        totalproc = total_process(procsattimeL)
        totalproc.write(totfile)

        # Assume monitor_process is last process standing
        if len(procsattimeL) == 1:
            break

        time.sleep(delay)

    totfile.close()
    sys.exit(0)



if __name__ == "__main__":
    main()
