# One run only. No continue/restart, native arguments, locals or full core dump.
set pagination off
set confirm off
set disable-randomization off
set debuginfod enabled off
set auto-load python-scripts off
set auto-load gdb-scripts off
set auto-load local-gdbinit off
set print frame-arguments none
set print elements 16
handle SIGPIPE nostop noprint pass
handle SIGSEGV SIGABRT SIGBUS SIGILL stop print nopass
run
python
import gdb
inferior = gdb.selected_inferior()
if inferior.pid:
    print("TASK01_GDB_STOPPED_INFERIOR_PID=%d" % inferior.pid)
    for command in ("info program", "p $_siginfo", "bt 30", "info threads", "thread apply all bt 6", "info sharedlibrary", "x/8i $pc"):
        print("TASK01_GDB_COMMAND=" + command)
        try:
            gdb.execute(command)
        except gdb.error as error:
            print("TASK01_GDB_CAPTURE_ERROR=" + str(error))
    gdb.execute("kill")
else:
    print("TASK01_GDB_NO_ACTIVE_INFERIOR: inspect exit status and launcher barrier; no native crash is presumed")
end
quit
