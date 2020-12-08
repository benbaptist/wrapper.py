import msgpack
import os
import threading
import time
import copy
import traceback
import shutil

# This version of Storify has been updated to
# remove JSON completely and add Python 3.x support.

class DummyLogger:
	def info(self): pass
	def debug(self): pass
	def error(self): pass
	def warning(self): pass
	def traceback(self): pass

class Storify:
	def __init__(self, root="data", log=DummyLogger()):
		self.root = root
		self.databases = []

		self.log = log

		if not os.path.exists(self.root):
			os.makedirs(self.root)

		if not os.path.exists(os.path.join(self.root, ".backups")):
			os.mkdir(os.path.join(self.root, ".backups"))

	def getDB(self, name):
		for database in self.databases:
			if database.name == name:
				return database

		db = Database(name, self.root, self.log)
		self.databases.append(db)

		return db

	def get_mini_db(self, path):
		for database in self.databases:
			if database.name == path and database.root == None:
				return database

		db = Database(path, None, self.log)
		self.databases.append(db)

		return db

	def tick(self, force=False):
		a = len(self.databases)
		i = 0
		while i < a:
			# Safely iterate through databases without any RuntimeErrors
			db = self.databases[i]

			if force:
				db.flush()
			else:
				if time.time() - db.lastFlush > 60 * 5: # Saves every 5 minutes
					db.flush()

			i += 1

	def flush(self):
		self.tick(force=True)

class Database:
	def __init__(self, name, root, log):
		self.name = name
		self.root = root
		self.log = log

		self.lastFlush = time.time()
		self.data = {}
		self.backupsAttentedTo = None # Unused
		self.backups = None

		if self.root:
			self.path = os.path.join(self.root, "%s.mpack" % self.name)
		else:
			self.path = self.name

		path_to, filename = os.path.split(self.path)
		self.backup_path = os.path.join(path_to, ".backups", self.name)

		if os.path.exists(self.path):
			try:
				self.data = self.unpack(self.path)
			except:
				self.log.traceback("Database '%s' corrupted, reading from backup..." % self.name)

				# Read from backups
				while True:
					backup = self.grabLastBackup()
					if backup == None:
						self.log.error("Unfortunately, no backup was found. Fresh start!")
						return

					try:
						self.log.warning("Reading from backup `%s`..." % backup)
						self.data = self.unpack(backup)
						break
					except:
						continue

			return

	def unpack(self, path):
		with open(path, "rb") as f:
			blob = f.read()
			try:
				return msgpack.unpackb(blob, encoding="utf-8")
			except TypeError:
				return msgpack.unpackb(blob)

	def grabLatestBackup(self):
		if not os.path.exists(self.backup_path):
			os.makedirs(self.backup_path)
			return 0

		self.backups = os.listdir(self.backup_path)
		self.backups = [int(i) for i in self.backups]
		self.backups.sort()
		self.backups.reverse()

		if len(self.backups) > 0:
			return int(self.backups[0])
		else:
			return 0

	def grabLastBackup(self):
		if self.backups == None:
			if not os.path.exists(self.backup_path):
				return

			self.backups = os.listdir(self.backup_path)
			self.backups = [int(i) for i in self.backups]
			self.backups.sort()
			self.backups.reverse()

		if len(self.backups) < 1:
			return

		backup = str(self.backups[0])
		del self.backups[0]

		return os.path.join(self.backup_path, backup)

	def flush(self):
		# Backup before flushing
		if os.path.exists(self.path):
			self.log.debug("Backing up %s" % self.name)
			backupID = str(self.grabLatestBackup() + 1)

			try:
				shutil.copy(self.path, os.path.join(self.backup_path, backupID))
			except IOError:
				self.log.traceback("Possibly out of space, aggressively deleting overly-redundant backups...")

				while len(self.backups) > 7:
					self.log.debug("Deleting backup %s/%s..." % (self.name, self.backups[0]))
					os.remove(os.path.join(self.backup_path, str(self.backups[0])))
					del self.backups[0]

				return

			self.backups = os.listdir(self.backup_path)
			self.backups = [int(i) for i in self.backups]
			self.backups.sort()

			while len(self.backups) > 30:
				self.log.debug("Deleting backup %s/%s..." % (self.name, self.backups[0]))
				os.remove(
					os.path.join(self.backup_path, str(self.backups[0]))
				)
				del self.backups[0]

		try:
			with open(self.path + ".tmp", "wb") as f:
				self.log.debug("Syncing '%s' to disk" % self.name)
				f.write(msgpack.packb(self.data))

			shutil.move(self.path + ".tmp", self.path)

			self.lastFlush = time.time()
		except IOError:
			self.log.error(
				"IOError thrown... not sure how to handle this one. "
				"Hopefully some space is made before the program goes down "
				"to ensure this data gets written.")

			if os.path.exists(self.path + ".tmp"):
				self.log.debug("Cleaning up temporary file")
				os.remove(self.path + ".tmp")

	def __getitem__(self, index):
		if not (type(index) in (str, bytes)):
			raise TypeError("Expected str or bytes, got '%s'" % type(index))
		return self.data[index]

	def __setitem__(self, index, value):
		if not (type(index) in (str, bytes)):
			raise TypeError("Expected str or bytes, got '%s'" % type(index))
		self.data[index] = value
		return self.data[index]

	def __delattr__(self, index):
		if not (type(index) in (str, bytes)):
			raise TypeError("Expected str or bytes, got '%s'" % type(index))
		del self.data[index]

	def __delitem__(self, index):
		if not (type(index) in (str, bytes)):
			raise TypeError("Expected str or bytes, got '%s'" % type(index))
		del self.data[index]

	def __iter__(self):
		for i in self.data:
			yield i
