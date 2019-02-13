from main import *

folder_base = "/home/chris/Projects/YoutubeTextAnalytics/"

links = [ #test vid for now
	"https://www.youtube.com/watch?v=pUncXbXAiV0"
]

critical_role  = YoutubeTextAnalytics(folder_base, links)

critical_role.full_run()