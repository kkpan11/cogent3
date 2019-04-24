import time
import functools
from tqdm import tqdm
from cogent3.util import parallel2

__author__ = "Sheng Han Moses Koh"
__copyright__ = ""
__credits__ = ["Peter Maxwell", "Sheng Han Moses Koh"]
__license__ = "GPL"
__version__ = ""


class ProgressContext(object):

    def __init__(self, show_progress=True, prefix=None, base=0.0, segment=1.0,
                 rate=1.0):
        if show_progress:
            progress_bar = tqdm(total=1, leave=False,
                                bar_format='{desc} {percentage:3.0f}%|{bar}| '
                                           '{n_fmt:.10}/{total_fmt} '
                                           '[{rate_fmt}{postfix}]')
        else:
            progress_bar = None
        self.progress_bar = progress_bar
        self.progress = 0
        self.msg = ''
        self.prefix = prefix or []
        self.message = self.prefix + [self.msg]
        self._max_text_len = 0
        self.max_depth = 2
        self.rate = rate

    def display(self, msg=None, progress=None):
        if self.progress_bar:
            updated = False
            if progress is not None:
                self.progress = min(progress, 1.0)
                self.progress_bar.n = self.progress
                updated = True
            else:
                self.progress_bar.n = 1
            if msg is not None and msg != self.msg:
                self.msg = self.message[-1] = msg
                self.progress_bar.set_description(self.message[0],
                                                  refresh=False)
                updated = True
            if updated:
                self.render(progress)

    def render(self, progress=True):
        if self.progress_bar:
            self.progress_bar.refresh()

    def done(self):
        if self.progress_bar:
            self.progress_bar.close()
            self.progress_bar = None

    def series(self, items, noun='', labels=None, start=None, end=1.0,
               count=None):
        """Wrap a looped-over list with a progress bar"""
        if count is None:
            if not hasattr(items, '__len__'):
                items = list(items)
            count = len(items)
        if start is None:
            start = 0.0
        step = (end - start) / count
        if labels:
            assert len(labels) == count
        elif count == 1:
            labels = ['']
        else:
            if noun:
                noun += ' '
            template = '%s%%%sd/%s' % (noun, len(str(count)), count)
            labels = [template % i for i in range(0, count)]
        for (i, item) in enumerate(items):
            self.display(msg=labels[i], progress=start +
                                                 step * i)
            yield item
        self.display(progress=end)

    def imap(self, f, s, workers=None, pure=True, **kw):
        if pure:
            results = parallel2.map(f, s, workers)
        else:
            results = map(f, s)
        for result in self.series(results, count=len(s), **kw):
            yield result

    def map(self, f, s, **kw):
        return list(self.imap(f, s, **kw))


def display_wrap(slow_function):
    """Decorator which give the function its own UI context.
    The function will receive an extra argument, 'ui',
    which is used to report progress etc."""

    @functools.wraps(slow_function)
    def f(*args, **kw):
        show_progress = kw.pop('show_progress', None)
        prog_display = ProgressContext(show_progress=show_progress, rate=0.1)
        kw['ui'] = prog_display
        try:
            result = slow_function(*args, **kw)
        finally:
            prog_display.done()
        return result

    return f


@display_wrap
def subdemo(ui):
    for j in ui.series(list(range(10))):
        time.sleep(0.1)
    return


@display_wrap
def demo(ui):
    print("non-linebuffered output, tricky but look:", end=' ')
    for i in ui.series(list(range(10))):
        time.sleep(.6)
        if i == 5:
            print('\nhalfway through, a new line: ', end=' ')
        if i % 2:
            subdemo()
        print(i, ".", end=' ')
    print("done")

if __name__ == '__main__':
    demo()