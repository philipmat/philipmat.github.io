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
	require 'fileutils'
	puts file + " => ./_posts/#{date.to_s}-" + File.basename(file)
	FileUtils.mv(file, "./_posts/#{date.to_s}-" + File.basename(file))
	# TODO: update the header in the file
end

desc 'DreamHost tasks'
namespace :dh do
	@params = %w[-avze ssh --delete _site/]
	@dh = "dreamhost:~/philipm.at/"
	task :testupload do
		system(['rsync','--dry-run',@params,@dh].join(' '))
	end
	task :upload do
		system(['rsync',@params,@dh].join(' '))
	end
end
