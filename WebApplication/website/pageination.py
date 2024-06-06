from django.utils.safestring import mark_safe
from django.http.request import QueryDict
import copy


class Pagination(object):
    
    def __init__(self, request, search, page_param="page", page_size=5, plus =5, ):
        
        
        query_dict = copy.deepcopy(request.GET)
        query_dict._mutable = True
        
        self.query_dict =  query_dict
        
        query_dict.setlist('page',[2])
        print(query_dict.urlencode())
        
        self.page_param = page_param
        page = request.GET.get(page_param, "1")
        if page.isdecimal():
            page = int(page)
        else:
            page = 1
        
        self.page = page
        self.page_size = page_size
     
        self.start = (page-1) * page_size
        self.end = page * page_size
        
        self.search = search[self.start:self.end]
        
         # total page
        total_count=search.count()
        page_total, div = divmod(total_count,page_size)
        if div:
            page_total+=1
        
        self.page_total = page_total
        self.plus = plus
        
    
    def html(self):
         # current page + - 5
        
        if self.page_total <= 2*self.plus+1:
            start_page = 1
            end_page = self.page_total
        else:
            # current page<plus
            if self.page <= self.plus:
                start_page =1
                end_page=2*self.plus+1
            else:
            # current page>plus
                if (self.page + self.plus)>self.page_total:
                    start_page = self.page_total -2*self.plus
                    end_page = self.page_total
                else:
                    start_page = self.page - self.plus
                    end_page = self.page + self.plus
                    
        page_str_list = []
        
        # first page 
        self.query_dict.setlist(self.page_param,[1])
        first_page = '<li class="page-item"><a class="page-link" href="?{}" aria-label="Previous">First</a></li>'.format(self.query_dict.urlencode())
        page_str_list.append(first_page)
        
        # previous 
        if self.page > 1:
            self.query_dict.setlist(self.page_param,[self.page-1])
            prev = '<li class="page-item"><a class="page-link" href="?{}" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li>'.format(self.query_dict.urlencode())
        else:
            self.query_dict.setlist(self.page_param,[1])
            prev = '<li class="page-item"><a class="page-link" href="?{}" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li>'.format(self.query_dict.urlencode())
        page_str_list.append(prev)
        
        # page
        for i in range(start_page, end_page+1):
            self.query_dict.setlist(self.page_param,[i])
            if i == self.page:
                page_genertate = '<li class="page-item active"><a class="page-link" href="?{}">{}</a></li>'.format(self.query_dict.urlencode(), i)
            else:
                page_genertate = '<li class="page-item"><a class="page-link" href="?{}">{}</a></li>'.format(self.query_dict.urlencode(), i)
            page_str_list.append(page_genertate)
            
        # next
        if 1< self.page < self.page_total:
            self.query_dict.setlist(self.page_param,[self.page+1])
            next = '<li class="page-item"><a class="page-link" href="?{}" aria-label="Next"><span aria-hidden="true">&raquo;</span></a></li>'.format(self.query_dict.urlencode())
        else:
            self.query_dict.setlist(self.page_param,[self.page_total])
            next = '<li class="page-item"><a class="page-link" href="?{}" aria-label="Next"><span aria-hidden="true">&raquo;</span></a></li>'.format(self.query_dict.urlencode())
        page_str_list.append(next)
        
        #last page
        self.query_dict.setlist(self.page_param,[self.page_total])
        last_page = '<li class="page-item"><a class="page-link" href="?{}" aria-label="Previous">Last</a></li>'.format(self.query_dict.urlencode())
        page_str_list.append(last_page)
            
        page_string = mark_safe( "".join(page_str_list))
        
        return page_string
        