import logging
import subprocess

logger = logging.getLogger(__name__)

class Resource:
    def __init__(self, command, source, output, suffix=None, recursive=False, pattern='*'):
        self.command = command
        self.source = source
        self.output = output
        self.suffix = suffix
        self.recursive = recursive
        self.pattern = pattern

    def run(self):
        l = list(self.source.iterdir())
        while len(l) > 0:
            f = l.pop(0)
            if f.is_dir():
                if self.recursive:
                    l.extend(f.iterdir())
                continue
            if not f.match(self.pattern):
                continue
            dest = self.output / f.relative_to(self.source)
            if self.suffix is not None:
                dest = dest.with_suffix(self.suffix)
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                if dest.stat().st_mtime > f.stat().st_mtime:
                    logger.info('skip %s', dest)
                    continue
            except FileNotFoundError:
                pass

            with f.open('rb') as in_, dest.open('wb') as out:
                logger.info('%s <%s >%s', ' '.join(self.command), f, dest)
                r = subprocess.call(self.command, stdin=in_, stdout=out)
                if r != 0:
                    logger.error('%r: failed! (%d)', self.command, r)
                    raise Exception