from bpy.props import BoolProperty, CollectionProperty, StringProperty


def make_unique_name(name: str, names: list[str]) -> str:
    if name not in names:
        return name

    split = name.rsplit('.', 1)
    number = 0

    try:
        number = int(split[-1])
        name = split[0]
    except ValueError:
        pass

    name = f'{name}.{str(number + 1).zfill(3)}'

    return make_unique_name(name, names)


class DataItem:
    name: StringProperty()

    def compare(self, other) -> int:
        raise NotImplementedError()

    def on_add(self) -> None:
        raise NotImplementedError()

    def on_remove(self) -> None:
        raise NotImplementedError()

    def on_move(self, dst) -> None:
        raise NotImplementedError()


class DataCollection(DataItem):
    items: CollectionProperty()

    show_expanded: BoolProperty()

    def _key_to_index(self, key):
        if isinstance(key, int):
            if key < 0:
                return len(self.items) + key
            else:
                return key
        elif isinstance(key, str):
            return self.items.find(key)
        elif isinstance(key, DataItem):
            return self.items.find(key.name)

        return -1

    def add(self, name: str) -> DataItem:
        name = make_unique_name(name, self.items.keys())

        # Add item.
        item = self.items.add()
        item.on_add()
        item.name = name

        return item

    def remove(self, key: int | str | DataItem) -> bool:
        index = self._key_to_index(key)

        if index < 0 or index >= len(self.items):
            return False

        # Remove item.
        self.items[index].on_remove()
        self.items.remove(index)

        return True

    def move(self, src_key: int | str | DataItem, dst_key: int | str | DataItem) -> bool:
        src_index = self._key_to_index(src_key)
        dst_index = self._key_to_index(dst_key)

        if src_index == dst_index:
            return False
        elif src_index < 0 or src_index >= len(self.items):
            return False
        elif dst_index < 0 or dst_index >= len(self.items):
            return False

        # Move item.
        self.items[src_index].on_move(self.items[dst_index])
        self.items.move(src_index, dst_index)

        return True

    def compare(self, other):
        min_len = len(other.items)
        result = 1

        if len(self.items) == min_len:
            result = 0
        elif len(self.items) < min_len:
            min_len = len(other.items)
            result = -1

        for i in range(min_len):
            r = self.items[i].compare(other.items[i])

            if r != 0:
                return r

        return result

    def on_add(self):
        pass

    def on_remove(self):
        for item in reversed(self.items):
            item.on_remove()

    def on_move(self, dst):
        if self.items and dst.items:
            dst_item = dst.items[-1]
            src_item_itr = self.items

            if self.items[0].compare(dst_item) > 0:
                dst_item = dst.items[0]
                src_item_itr = reversed(self.items)

            for src_item in src_item_itr:
                src_item.on_move(dst_item)
                dst_item = src_item
