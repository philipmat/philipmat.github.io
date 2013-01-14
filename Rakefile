desc 'Running Jekyll with --auto --server'
task :dev do
	system('jekyll --auto --server')
end

desc 'Cleans up the output folder'
task :clean do
	require 'fileutils'
	FileUtils.rm_rf '_site'
	puts "Removed _site."
end

desc 'Build the sites folder'
task :build do
	system('jekyll')
end

desc 'Rebuild the _sites folder from the ground-up'
task :rebuild => [:clean, :build] do
end

desc 'List current drafts'
task :drafts do 
	Dir.glob('./drafts/*') { |x|
		puts "  " + File.basename(x)
	}
end

desc 'Promote a draft to published post.'
task :publish do
	files = Dir.glob('./drafts/*')
	if files.length == 0
		puts "No drafts."
		exit
	end
	puts "Drafts:"
	files.each_with_index { |f,i|
		puts "#{i+1}. " + File.basename(f)
	}
	print "Select a draft to publish: "
	draft = STDIN.gets
	draft.chomp!
	if draft == "" 
		puts "Nothing."
		exit
	end
	draft = draft.to_i - 1
	if draft < 0 || draft >= files.length
		puts "Not in range."
		exit
	end
	file = files[draft]
	print "Publish " + File.basename(file) + " as of today? [Y or other date]: "
	require 'date'
	date = STDIN.gets
	date.chomp!
	if date == "" || date == "Y"
		date = Date.today
	else
		# TODO: handle error
		date = Date.parse(date)
	end
	src = File.expand_path(file) 
	dest = File.expand_path("./_posts/#{date.to_s}-" + File.basename(file))
	puts "from #{src} \n to  #{dest}"
	File.rename(src, dest)
	# TODO: update the header in the file
end

desc 'PhilipM.at tasks'
namespace :pmat do
	@params = %w[-avze ssh --delete _site/ --include='.htaccess']
	@dh = "philipm.at:~/philipm.at/"
	desc 'Tests the philipm.at upload'
	task :testupload do
		command = ['rsync','--dry-run -v',@params,@dh].join(' ')
		puts "Executing: #{command}."
		system(command)
	end
	desc 'Uploads the site to philipm.at'
	task :upload do
		command = ['rsync',@params,@dh].join(' ')
		puts "Executing: #{command}."
		system(command)
	end
end
