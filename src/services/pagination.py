import math

class Pagination():
    def __init__(self, total_cred: int, page_size: int):

        self.total_cred = total_cred
        self.current_page: int = 1
        self.page_size: int = page_size
        self.offset: int = 0
    
    @property
    def total_pages(self):
        return math.ceil(self.total_cred / self.page_size)

    @property
    def showing_items_start(self) -> int:
        return ((self.current_page - 1) * self.page_size) + 1

    @property
    def showing_items_end(self) -> int:
        return min(self.current_page * self.page_size, self.total_cred)
        
    def next_page(self) -> None:
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.offset += self.page_size

    def previous_page(self) -> None:
        if self.current_page > 1:
            self.current_page -= 1
            self.offset -= self.page_size

    def reset_state(self):
        self.current_page = 1
        self.offset = 0