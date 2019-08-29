from django.db import models

#https://www.youtube.com/watch?v=-D6hVchRamk

class Post(models.Model):
	ids = models.BigIntegerField(primary_key=True)
	title = models.CharField(max_length=60) # размер поста
	text = models.TextField()

	def __str__(self):
		return str(self.ids) + '_' + str(self.title)
