import images


class BulletModel:
  def __init__(self, sprite, movable, destructible):
    self.sprite = sprite
    self.movable = movable
    self.destructible = destructible


def get_bullet():
  bullet = BulletModel(images.bullet, True, True)
  return bullet
