import hotshot, hotshot.stats
from solipsis.services.profile.gui.editor import run

print "launching profiler"
prof = hotshot.Profile("editor_launch.prof")
prof.runcall(run)
prof.close()
print "launching stats"
stats = hotshot.stats.load("editor_launch.prof")
stats.strip_dirs()
stats.sort_stats('cumulative')
stats.print_stats(20)
