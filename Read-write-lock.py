import threading, easygui, random, time
from queue import Queue
class RWLock:
        def __init__(self):
            self.wait_writers_q = Queue()
            self.rwlock = 0
            self.writers_waiting = 0
            self.monitor = threading.RLock()
            self.readers_ok = threading.Condition(self.monitor)
        def acquire_read(self):
            self.monitor.acquire()
            while self.rwlock < 0 or self.writers_waiting or self.rwlock == max:
              self.readers_ok.wait()
            self.rwlock += 1
            self.monitor.release()
        def acquire_write(self):
            self.monitor.acquire()
            while self.rwlock != 0:
              self.writers_waiting += 1
              writers_ok = threading.Condition(self.monitor)
              self.wait_writers_q.put(writers_ok)
              writers_ok.wait()
              self.writers_waiting -= 1
            self.rwlock = -1
            self.monitor.release()
        def promote(self):
            self.monitor.acquire()
            self.rwlock -= 1
            while self.rwlock != 0:
              self.writers_waiting += 1
              writers_ok = threading.Condition(self.monitor)
              self.wait_writers_q.put(writers_ok)
              writers_ok.wait()
              self.writers_waiting -= 1
            self.rwlock = -1
            self.monitor.release()
        def demote(self):
            self.monitor.acquire()
            self.rwlock = 1
            self.readers_ok.notifyAll()
            self.monitor.release()
        def release(self):
            self.monitor.acquire()
            if self.rwlock < 0:
              self.rwlock = 0
            else:
              self.rwlock -= 1
            wake_writers = self.writers_waiting and self.rwlock == 0
            wake_readers = self.writers_waiting == 0
            self.monitor.release()
            if wake_writers:
              writers_ok = self.wait_writers_q.get_nowait()
              writers_ok.acquire()
              writers_ok.notify()
              writers_ok.release()
            elif wake_readers:
              self.readers_ok.acquire()
              self.readers_ok.notifyAll()
              self.readers_ok.release()
if __name__ == '__main__':
        max = int(easygui.enterbox("how many readers can be at the same time?"))
        a = int(easygui.enterbox("how many Readers?"))
        b = int(easygui.enterbox("how many Writers?"))
        c = int(easygui.enterbox("how many ReaderWriters?"))
        d = int(easygui.enterbox("how many WriterReaders?"))
        rwl = RWLock()
        class Reader(threading.Thread):
          def run(self):
            print(self, 'apply')
            rwl.acquire_read()
            print(self, 'acquire')
            time.sleep(random.uniform(2, 5))
            print(self, 'stop')
            rwl.release()
        class Writer(threading.Thread):
          def run(self):
            print(self, 'apply')
            rwl.acquire_write()
            print(self, 'acquire')
            time.sleep(random.uniform(2, 5))
            print(self, 'stop')
            rwl.release()
            rwl.release()
        class ReaderWriter(threading.Thread):
          def run(self):
            print(self, 'apply')
            rwl.acquire_read()
            print(self, 'acquire')
            time.sleep(random.uniform(2, 5))
            rwl.promote()
            print(self, 'promote')
            time.sleep(random.uniform(2, 5))
            print(self, 'stop')
            rwl.release()
        class WriterReader(threading.Thread):
          def run(self):
            print(self, 'apply')
            rwl.acquire_write()
            print(self, 'acquire')
            time.sleep(random.uniform(2, 5))
            print(self, 'demote')
            rwl.demote()
            time.sleep(random.uniform(2, 5))
            print(self, 'stop')
            rwl.release()
        for i in range(a-1):
            Reader().start()
            time.sleep(random.uniform(1, 3))
        for i in range(c):
            ReaderWriter().start()
            time.sleep(random.uniform(1, 3))
        for i in range(d):
            WriterReader().start()
            time.sleep(random.uniform(1, 3))
        Reader().start()
        for i in range(b):
            Writer().start()
            time.sleep(random.uniform(1, 3))