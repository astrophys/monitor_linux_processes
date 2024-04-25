# Author : Ali Snedden
# Date   : 04/23/24
# License: MIT
# Notes :
#   Only works on linux
#
# To Do :
#   When I'm clever, I'll use inheritance with Process and CpuProcess / GpuProcess
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
    """Generic Process that is parent class of CpuProcess and GpuProcess"""
    def __init__(self, pid : int, percentcpu : float, percentmem : float,
                 localtime : str, timesecs : int, command : str):
        """Monitor user processes by using Python

        Args:

        Returns:

        Raises:
        """
        self.pid=pid
        self.percentcpu=percentcpu
        self.percentmem=percentmem
        self.localtime=localtime
        self.timesecs=timesecs
        self.command=command


class CpuProcess(Process):
    """Process from a user"""
    def __init__(self, pid : int, user : str, virt : str, res : str,
                 shr : str, state : str, percentcpu : float, percentmem : float,
                 localtime : str, timesecs : int, command : str):
        """Monitor user processes by using Python

        Args:

        Returns:

        Raises:
        """
        super().__init__(pid=pid, percentcpu=percentcpu, percentmem=percentmem,
                         localtime=localtime, timesecs=timesecs, command=command)
        self.user=user
        self.virt = -1
        self.res  = -1
        self.shr  = -1
        self.parse_mem(virt, 'virt')
        self.parse_mem(res, 'res')
        self.parse_mem(shr, 'shr')
        self.state=state


    def parse_mem(self, memstr : str, attr : str) :
        """Parse memory string from top, handle different units. Set attribute 'attr'

        Args:
            memstr : (str) string of memory taken from top

        Returns:
            N/A : sets self.attr = value

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
        except AttributeError :
            if type(memstr) == float:
                mem = memstr
        self.__setattr__(attr, mem)


    def write(self, fout) -> None :
        """Write out data to a file

        Args:
            fout : (file) open file to write to

        Returns:
            Nothing

        Raises:
        """
        fout.write("{:<18} : {:<8.1f} : {:<9} {:<5} {:<13.6f} {:<13.6f} {:<13.6f} "
                   "{:<6.2f} {:<6.2f} {}\n".format(self.localtime, self.timesecs,
                                        self.pid, self.user, self.virt, self.res,
                                        self.shr, self.percentcpu, self.percentmem,
                                        self.command))
        fout.flush()


class GpuProcess(Process):
    """GPU Process"""
    def __init__(self, pid : int, gpu : int, sm : str, mem, command : str,
                 localtime : str, timesecs : int):
        """Monitor gpu processes

        Args:

        Returns:

        Raises:
        """


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
    totproc = CpuProcess(pid = -1, user = proc.user, virt = virt, res = res,
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
    parser.add_argument('--outstem', metavar='output_path_stem', type=str,
                        help='Output path stem')
    args = parser.parse_args()
    user = args.user
    delay = args.delay
    start = time.time()
    startlocal = time.localtime()
    cpuprocL = []
    print("{}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(startlocal.tm_year,
          startlocal.tm_mon, startlocal.tm_mday, startlocal.tm_hour,
          startlocal.tm_min, startlocal.tm_sec))
    totfile = open("{}-total.txt".format(args.outstem), "w+")
    totfile.write("{:<18} : {:<8} : {:<9} {:<5} {:<13} {:<13} {:<13} {:<6} {:<6}"
                  "{}\n".format("Date", "time", "pid", "user", "virt", "res", "shr",
                              "%cpu", "%mem", "command"))
    allfile = open("{}-all.txt".format(args.outstem), "w+")
    allfile.write("{:<18} : {:<8} : {:<9} {:<5} {:<13} {:<13} {:<13} {:<6} {:<6}"
                  "{}\n".format("Date", "time", "pid", "user", "virt", "res", "shr",
                              "%cpu", "%mem", "command"))

    while True:
        # Should be careful of string injection
        # https://stackoverflow.com/a/28756533/4021436
        string="top -b -u {} -n 1 | grep {}".format(user,user)
        top = subprocess.getoutput(string)
        print(top)
        topL = top.split('\n')
        cpuprocsattimeL = []       # procs ONLY at this current time
        # Get time
        localtime = time.localtime()
        localtime = "{}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(localtime.tm_year,
                    localtime.tm_mon, localtime.tm_mday, localtime.tm_hour,
                    localtime.tm_min, localtime.tm_sec)
        timesecs = time.time() - start
        for line in topL:
            line = line.split()
            cpuproc = CpuProcess(pid=int(line[0]), user=line[1], virt=line[4],
                              res=line[5], shr=line[6], state=line[7],
                              percentcpu=float(line[8]), percentmem=float(line[9]),
                              localtime=localtime, timesecs=timesecs,
                              command = line[-1])
            cpuproc.write(allfile)
            cpuprocL.append(cpuproc)
            cpuprocsattimeL.append(cpuproc)
        totalcpuproc = total_process(cpuprocsattimeL)
        totalcpuproc.write(totfile)

        # Assume monitor_process is last process standing
        if len(cpuprocsattimeL) == 1:
            break

        time.sleep(delay)

    totfile.close()
    sys.exit(0)



if __name__ == "__main__":
    main()
