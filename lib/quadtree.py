class QuadTree(object):
    """An implementation of a quad-tree.
 
    This QuadTree started life as a version of [1] but found a life of its own
    when I realised it wasn't doing what I needed. It is intended for static
    geometry, ie, items such as the landscape that don't move.
 
    This implementation inserts items at the current level if they overlap all
    4 sub-quadrants, otherwise it inserts them recursively into the one or two
    sub-quadrants that they overlap.
 
    Items being stored in the tree must possess the following attributes:
 
        left - the x coordinate of the left edge of the item's bounding box.
        top - the y coordinate of the top edge of the item's bounding box.
        right - the x coordinate of the right edge of the item's bounding box.
        bottom - the y coordinate of the bottom edge of the item's bounding box.
 
        where left &lt; right and top &lt; bottom
        
    ...and they must be hashable.
    
    Acknowledgements:
    [1] http://mu.arete.cc/pcr/syntax/quadtree/1/quadtree.py
    """
    def __init__(self, items=[], depth=6, boundingRect=None):
        """Creates a quad-tree.
 
        @param items:
            A sequence of items to store in the quad-tree. Note that these
            items must possess left, top, right and bottom attributes.
            The sequence can be an empty list, but do give a bounding rectangle
            if it is.
            
        @param depth:
            The maximum recursion depth.
            
        @param boundingRect:
            The bounding rectangle of all of the items in the quad-tree. For
            internal use only.
        """
        # The sub-quadrants are empty to start with.
        self.nw = self.ne = self.se = self.sw = None
        
        # If we've reached the maximum depth then insert all items into this
        # quadrant.
        self.depth = depth
        if self.depth == 0:
            self.items = items
            return
        
        # Find this quadrant's centre.
        if boundingRect:
            l, t, r, b = self.l, self.t, self.r, self.b = boundingRect
        else:
            # If there isn't a bounding rect, then calculate it from the items.
            l = self.l = min(item.rect.left for item in items)
            t = self.t = min(item.rect.top for item in items)
            r = self.r = max(item.rect.right for item in items)
            b = self.b = max(item.rect.bottom for item in items)
        cx = self.cx = (l + r) * 0.5
        cy = self.cy = (t + b) * 0.5
        
        self.items = []
        if not items:
            return
        nw_items = []
        ne_items = []
        se_items = []
        sw_items = []
        
        for item in items:
            # Which of the sub-quadrants does the item overlap?
            in_nw = item.rect.left <= cx and item.rect.top <= cy
            in_sw = item.rect.left <= cx and item.rect.bottom >= cy
            in_ne = item.rect.right >= cx and item.rect.top <= cy
            in_se = item.rect.right >= cx and item.rect.bottom >= cy
                
            # If it overlaps all 4 quadrants then insert it at the current
            # depth, otherwise append it to a list to be inserted under every
            # quadrant that it overlaps.
            if in_nw and in_ne and in_se and in_sw:
                self.items.append(item)
            else:
                if in_nw: nw_items.append(item)
                if in_ne: ne_items.append(item)
                if in_se: se_items.append(item)
                if in_sw: sw_items.append(item)
            
        # Create the sub-quadrants, recursively.
        if nw_items:
            self.nw = QuadTree(nw_items, self.depth-1, (l, t, cx, cy))
        if ne_items:
            self.ne = QuadTree(ne_items, self.depth-1, (cx, t, r, cy))
        if se_items:
            self.se = QuadTree(se_items, self.depth-1, (cx, cy, r, b))
        if sw_items:
            self.sw = QuadTree(sw_items, self.depth-1, (l, cy, cx, b))
    
    def insert(self, item):
        """Inserts an item in a quad-tree.
 
        @param item:
            An item to store in the quad-tree. Note that this item
            must possess left, top, right and bottom attributes.
        """
        # If we've reached the maximum depth then insert item in this quadrant.
        if self.depth == 0:
            self.items.append(item)
            return
        
        in_nw = item.rect.left <= self.cx and item.rect.top <= self.cy
        in_sw = item.rect.left <= self.cx and item.rect.bottom >= self.cy
        in_ne = item.rect.right >= self.cx and item.rect.top <= self.cy
        in_se = item.rect.right >= self.cx and item.rect.bottom >= self.cy
        
        # If it overlaps all 4 quadrants then insert it at the current
        # depth, otherwise append it to the item list of every quadrant
        # that it overlaps.
        if in_nw and in_ne and in_se and in_sw:
            self.items.append(item)
        else:
            if in_nw:
                if self.nw:
                    self.nw.insert(item)
                else:
                    self.nw = QuadTree([item], self.depth-1,
                                       (self.l, self.t, self.cx, self.cy))
            if in_ne:
                if self.ne:
                    self.ne.insert(item)
                else:
                    self.ne = QuadTree([item], self.depth-1,
                                       (self.cx, self.t, self.r, self.cy))
            if in_se:
                if self.se:
                    self.se.insert(item)
                else:
                    self.se = QuadTree([item], self.depth-1,
                                       (self.cx, self.cy, self.r, self.b))
            if in_sw:
                if self.sw:
                    self.sw.insert(item)
                else:
                    self.sw = QuadTree([item], self.depth-1,
                                       (self.l, self.cy, self.cx, self.b))
    
    def remove(self, item):
        """Removes an item from a quad-tree.
 
        @param item:
            Whatever object was succesfully inserted in this tree
        """
        # If we've reached the maximum depth remove the itam from this quadrant.
        if self.depth == 0:
            self.items.remove(item)
            return
        
        in_nw = item.rect.left <= self.cx and item.rect.top <= self.cy
        in_sw = item.rect.left <= self.cx and item.rect.bottom >= self.cy
        in_ne = item.rect.right >= self.cx and item.rect.top <= self.cy
        in_se = item.rect.right >= self.cx and item.rect.bottom >= self.cy
        
        # If it overlaps all 4 quadrants remove it, otherwise
        # search the lower quadrants for it
        if in_nw and in_ne and in_se and in_sw:
            self.items.remove(item)
        else:
            if in_nw and self.nw:
                self.nw.remove(item)
            if in_ne and self.ne:
                self.ne.remove(item)
            if in_se and self.se:
                self.se.remove(item)
            if in_sw and self.sw:
                self.sw.remove(item)
    
    def hitPoint(self, x, y):
        # Find the hits at the current level.
        hits = set(item for item in self.items if item.rect.collidepoint((x, y)))
        
        # Recursively check the lower quadrants.
        if self.nw and x <= self.cx and y <= self.cy:
            hits |= self.nw.hitPoint(x, y)
        if self.sw and x <= self.cx and y >= self.cy:
            hits |= self.sw.hitPoint(x, y)
        if self.ne and x >= self.cx and y <= self.cy:
            hits |= self.ne.hitPoint(x, y)
        if self.se and x >= self.cx and y >= self.cy:
            hits |= self.se.hitPoint(x, y)
        
        return hits
    
    def hit(self, rect):
        """Returns the items that overlap a bounding rectangle.
 
        Returns the set of all items in the quad-tree that overlap with a
        bounding rectangle.
        
        @param rect:
            The bounding rectangle being tested against the quad-tree. This
            must be a pyGame Rect, or an object having one as its rect attribute.
        """
        # Find the hits at the current level.
        hits = set(self.items[n] for n in rect.collidelistall(self.items))
        
        # Recursively check the lower quadrants.
        if self.nw and rect.left <= self.cx and rect.top <= self.cy:
            hits |= self.nw.hit(rect)
        if self.sw and rect.left <= self.cx and rect.bottom >= self.cy:
            hits |= self.sw.hit(rect)
        if self.ne and rect.right >= self.cx and rect.top <= self.cy:
            hits |= self.ne.hit(rect)
        if self.se and rect.right >= self.cx and rect.bottom >= self.cy:
            hits |= self.se.hit(rect)
 
        return hits
    
    def clear(self):
        self.items = []
        self.nw = None
        self.sw = None
        self.ne = None
        self.se = None
