# monitor_linux_processes
Python code to monitor linux user processes using `top` and `nvidia-smi`


### Usage :

Monitor :
```
./monitor_processes.py --user ali --delay 10 --outstem myoutput --verbose False  &
```

If you are submitting this with a batch script, you'll want to explicitly kill it

Plotting :
```
plot_data.py --data total_data  --output
```


### Installation :

Requirements : 
1. Python-3.X 
2. A computer with NVidia gpus and `nvidia-smi` installed
3. Linux operating system


### Future :
1. Make this gpu optional
