import praw
import time
import threading


now_time = time.time()


class bot:
	# defined variables
	def __init__(self):
		self.sub = # enter name of subreddit
		self.id = # enter user ID
		self.secret = # enter user secret ID
		self.username = # enter user username
		self.password = # enter user password
		self.user_agent = 'Flairbot/0.1 by Mandjevant'
		self.reddit = praw.Reddit(client_id = self.id, client_secret = self.secret, password = self.password, user_agent = self.user_agent, username = self.username)

		self.time_removal = 1800
		self.time_flair = 180																																							
		self.flair_message =  ('Your post does not have a flair and will soon be removed. Please add a flair within ' + str(int(self.time_removal/60)) + ' minutes or your post will be removed. This was an automated action by the r/worldpolitics moderation team.')
		self.removal_message = ('Your post was removed because a flair was not set in time.')																							
		self.removal_title = ('No flair')																																				
		self.removal_type = ('public')	

		self.loggingdict = {}


	# takes submission ID to reply to in the form of a comment
	# returns the comment ID
	def comment(self, submission):
		sm = submission.reply(self.flair_message)
		sm.mod.distinguish(sticky=True)
		return sm.id


	# takes comment ID to remove the comment
	def comment_remove(self, comment):
		self.reddit.comment(comment).delete()							


	# takes submission ID to remove the submission
	def post_remove(self, submission):
		self.reddit.submission(submission).mod.remove()																						
		self.reddit.submission(submission).mod.send_removal_message(message = self.removal_message, title = self.removal_title, type = self.removal_type)	


	# takes submission ID to update loggingdict if submission is not yet present
	def add_to_dict(self, submission):
		if submission in self.loggingdict.keys():
			pass
		else:
			self.loggingdict.update({submission: [self.comment(submission), time.time()]})


	# checks submissions in new once/minute to see if flair has yet to be set
	def new_flair_check(self):	
		print('thread 1 running')	
		try: 												
			start_time = time.time()		

			while True:				
				for submission in self.reddit.subreddit(self.sub).new(limit=100): 
					if submission.link_flair_text == None and (time.time() - submission.created_utc) > self.time_flair and (time.time() - submission.created_utc) <= 600:
						self.add_to_dict(submission) 
					else:
						continue

				time.sleep(60.0 - ((time.time() - start_time) % 60.0)) 	

		except KeyboardInterrupt:
			pass


	# checks submissions in loggingdict once/minute to see if flair is put
	# also handles exeptions 
	def responses_check(self):
		print('thread 2 running')
		try: 												
			start_time = time.time()		

			while True:																		
				for key, value in self.loggingdict.copy().items():
					submission = self.reddit.submission(id=key)
					currentpostflair = submission.link_flair_text
					comment = value[0] #praw.models.Comment(reddit=self.reddit, id=value[0])
					post_time = value[1]

					if (((time.time() - post_time) >= self.time_removal) and ((time.time() - post_time) < self.time_removal + 300)):
						if currentpostflair == None:
							try:
								self.comment_remove(comment)
							except:
								print('comment already removed')
							try:
								self.post_remove(submission)
							except:
								print('post already removed')
							self.loggingdict.pop(submission)
						else:
							try:
								self.comment_remove(comment)
							except:
								print('comment already removed')
							self.loggingdict.pop(submission)

					elif (time.time() - post_time) < self.time_removal:
						if not(currentpostflair == None):
							try:
								self.comment_remove(comment)
							except:
								print('comment already removed')
							self.loggingdict.pop(submission)
						else:
							continue

				time.sleep(60.0 - ((time.time() - start_time) % 60.0)) 	

			for key, value in self.loggingdict.items():
				if (time.time() - value[1]) > 7200:
					self.loggingdict.pop(key)

		except KeyboardInterrupt:
			pass


	# threading to execute functions in parallel
	def threading(self):
		a = threading.Thread(target=self.new_flair_check, name='Thread-a', daemon=True)		
		b = threading.Thread(target=self.responses_check, name='Thread-b', daemon=True)		

		a.start()																		
		b.start()																		

		a.join()																		
		b.join()


if __name__ == '__main__':
	bot().threading()

	print('Processing time:', time.time() - now_time)


