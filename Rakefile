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

desc 'Promote a draft to published post.'
task :publish do
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
