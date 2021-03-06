desc 'Running Jekyll with serve --watch'
task :dev do
	system('jekyll serve --watch')
end

desc 'Cleans up the output folder'
task :clean do
	require 'fileutils'
	FileUtils.rm_rf '_site'
	puts "Removed _site."
end

desc 'Build the sites folder'
task :build do
	system('jekyll build')
end

desc 'Rebuild the _sites folder from the ground-up'
task :rebuild => [:clean, :build] do
end

desc 'List current drafts'
task :drafts, :file, :op do |t, args|
	file = select_file('draft', 'drafts', args[:file])
	puts args
	op = args[:op]
	if not file
		return
	end
	
	if not op 
		print "(P)ublish, (E)dit, (D)elete: "
		op = STDIN.gets.chomp
	end
	op.upcase!
	op_task = nil
	case op
	when 'P'
		op_task = :publish
	when 'E'
		op_task = :edit
	when 'D'
		op_task = :delete
	end
	Rake::Task[op_task].invoke(file)
end

desc 'Promote a draft to published post.'
task :publish, :file do |t, args|
	file = args[:file]
	if not file
		return
	end
	print "Publish " + File.basename(file) + " as of today? [Y or other date]: "
	require 'date'
	date = STDIN.gets.chomp
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

desc 'Edits a draft.'
task :edit, :file do |t, args|
	file = args[:file]
	if not file
		return
	end
	editor = ENV['EDITOR']	
	# if I don't put this in, it doesn't stop on the next one
	# STDIN.getc.upcase
	print "Edit with #{editor}? [Y or other editor]: "
	ed = STDIN.gets
	ed.chomp!
	if ed.upcase == 'Y' || ed == ''
		ed = editor
	end
	command = "#{ed} #{file}"
	system(command)
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

def select_file(type, folder, file) 
	# is this a real file?
	actual = File.join(folder, file || '')
	if File.file?(actual)
		puts "File #{actual} exists."
		return File.absolute_path(actual)
	end

	# doesn't. maybe file is a partial
	files = Dir.glob("./#{folder}/#{file}*")
	if files.count == 1
		return files[0]
	end
	files.each_with_index { |x, i|
		puts "#{i+1}.  " + File.basename(x)
	}
	print "Select a #{type}: "
	draft = STDIN.gets.chomp
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
end
