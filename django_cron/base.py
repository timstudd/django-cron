"""
Copyright (c) 2007-2008, Dj Gilcrease
All rights reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import traceback, sys
import cPickle
from threading import Timer

from django.dispatch import dispatcher
from django.conf import settings
from django.utils import timezone

from signals import cron_done
import models

polling_frequency = getattr(settings, "CRON_POLLING_FREQUENCY", 15)

class Job(object):
	# 86400 seconds == 24 hours
	run_every = 86400

	def run(self, *args, **kwargs):  
		self.job()
		cron_done.send(sender=self, *args, **kwargs)
		
	def job(self):
		"""
		Should be overridden (this way is cleaner, but the old way - overriding run() - will still work)
		"""
		pass

class CronScheduler(object):


	def register(self, job_class, *args, **kwargs):
		"""
		Register the given Job with the scheduler class
		"""
		
		job_instance = job_class()
		
		if not isinstance(job_instance, Job):
			raise TypeError("You can only register a Job not a %r" % job_class)

		job, created = models.Job.objects.get_or_create(name=str(job_instance.__class__))
		if created:
			job.instance = cPickle.dumps(job_instance)
		job.args = cPickle.dumps(args)
		job.kwargs = cPickle.dumps(kwargs)
		job.run_frequency = job_instance.run_every
		job.save()

	def execute(self):
		"""
		Queue all Jobs for execution
		"""
		status, created = models.Cron.objects.get_or_create(pk=1)
		
		if status.executing:
			return

		status.executing = True
		status.save()

		jobs = models.Job.objects.all()
		for job in jobs:
			if job.queued:
				time_delta = timezone.now() - job.last_run
				if (time_delta.seconds + 86400*time_delta.days) > job.run_frequency:
					inst = cPickle.loads(str(job.instance))
					args = cPickle.loads(str(job.args))
					kwargs = cPickle.loads(str(job.kwargs))
					
					try:
						inst.run(*args, **kwargs)
						job.last_run = timezone.now()
						job.save()
						
					except Exception as e:
						print("Exception running task:", e)
						traceback.print_exc(file=sys.stdout)

		status.executing = False
		status.save()
		
		# Set up for this function to run again
		Timer(polling_frequency, self.execute).start()

def resetExecution(*args):
	status, created = models.Cron.objects.get_or_create(pk=1)
	if status.executing:
		status.executing = False
		status.save()

cronScheduler = CronScheduler()