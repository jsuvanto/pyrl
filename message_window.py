import curses

from window import Window
from textwrap import TextWrapper
from const.game import MORE_STR, DEFAULT


class MessageBar(Window):
	"""Handles the messaging bar system."""

	def __init__(self, window):
		super(MessageBar, self).__init__(window)

		self.msgqueue = ""

		#accommodate for printing the newline character
		self.wrapper = TextWrapper(width=(self.cols))

		#accommodate for the more_str if the messages continue on the next page
		self.last_line_wrapper = TextWrapper(width=(self.cols -
													len(MORE_STR) - 1))

	def update(self):
		self.print_queue()
		Window.update(self)

	def queue_msg(self, str):
		if len(str) > 0:
			self.msgqueue += str + " "

	def print_queue(self):
		self.clear()
		str = self.msgqueue
		cur_line = 0
		skip_all = False
		while True:
			if cur_line < self.rows - 1:
				if len(str) <= self.cols:
					self.w.addstr(cur_line, 0, str)
					break
				else:
					a = self.wrapper.wrap(str)
					self.w.addstr(cur_line, 0, a[0])
					str = " ".join(a[1:])
					cur_line += 1
			elif cur_line == self.rows - 1:
				if len(str) < self.cols:
					self.w.addstr(cur_line, 0, str)
					break
				else:
					a = self.last_line_wrapper.wrap(str)
					self.w.addstr(cur_line, 0, a[0] + MORE_STR)
					if not skip_all:
						c = self.sel_getch(char_list=DEFAULT)
						if c == ord('\n'):
							skip_all = True
					str = " ".join(a[1:])
					cur_line = 0
					self.clear()
		self.msgqueue = ""