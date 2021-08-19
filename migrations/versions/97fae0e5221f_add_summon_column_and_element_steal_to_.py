"""Add summon column and element steal to Weapon Table

Revision ID: 97fae0e5221f
Revises: 5b08239ecb0e
Create Date: 2021-08-18 20:33:57.392669

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '97fae0e5221f'
down_revision = '5b08239ecb0e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('weapon', sa.Column('min_attack_neutral_damage', sa.Integer(), nullable=True))
    op.add_column('weapon', sa.Column('max_attack_neutral_damage', sa.Integer(), nullable=True))
    op.add_column('weapon', sa.Column('min_attack_fire_damage', sa.Integer(), nullable=True))
    op.add_column('weapon', sa.Column('max_attack_fire_damage', sa.Integer(), nullable=True))
    op.add_column('weapon', sa.Column('min_attack_water_damage', sa.Integer(), nullable=True))
    op.add_column('weapon', sa.Column('max_attack_water_damage', sa.Integer(), nullable=True))
    op.add_column('weapon', sa.Column('min_attack_earth_damage', sa.Integer(), nullable=True))
    op.add_column('weapon', sa.Column('max_attack_earth_damage', sa.Integer(), nullable=True))
    op.add_column('weapon', sa.Column('min_attack_air_damage', sa.Integer(), nullable=True))
    op.add_column('weapon', sa.Column('max_attack_air_damage', sa.Integer(), nullable=True))
    op.add_column('weapon', sa.Column('min_attack_neutral_steal', sa.Integer(), nullable=True))
    op.add_column('weapon', sa.Column('max_attack_neutral_steal', sa.Integer(), nullable=True))
    op.add_column('weapon', sa.Column('min_attack_fire_steal', sa.Integer(), nullable=True))
    op.add_column('weapon', sa.Column('max_attack_fire_steal', sa.Integer(), nullable=True))
    op.add_column('weapon', sa.Column('min_attack_water_steal', sa.Integer(), nullable=True))
    op.add_column('weapon', sa.Column('max_attack_water_steal', sa.Integer(), nullable=True))
    op.add_column('weapon', sa.Column('min_attack_earth_steal', sa.Integer(), nullable=True))
    op.add_column('weapon', sa.Column('max_attack_earth_steal', sa.Integer(), nullable=True))
    op.add_column('weapon', sa.Column('min_attack_air_steal', sa.Integer(), nullable=True))
    op.add_column('weapon', sa.Column('max_attack_air_steal', sa.Integer(), nullable=True))
    op.add_column('weapon', sa.Column('min_attack_hp_steal', sa.Integer(), nullable=True))
    op.add_column('weapon', sa.Column('max_attack_hp_steal', sa.Integer(), nullable=True))
    op.add_column('weapon', sa.Column('min_summons', sa.Integer(), nullable=True))
    op.add_column('weapon', sa.Column('max_summons', sa.Integer(), nullable=True))
    op.add_column('weapon', sa.Column('is_hunting_weapon', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('weapon', 'is_hunting_weapon')
    op.drop_column('weapon', 'max_summons')
    op.drop_column('weapon', 'min_summons')
    op.drop_column('weapon', 'max_attack_hp_steal')
    op.drop_column('weapon', 'min_attack_hp_steal')
    op.drop_column('weapon', 'max_attack_air_steal')
    op.drop_column('weapon', 'min_attack_air_steal')
    op.drop_column('weapon', 'max_attack_earth_steal')
    op.drop_column('weapon', 'min_attack_earth_steal')
    op.drop_column('weapon', 'max_attack_water_steal')
    op.drop_column('weapon', 'min_attack_water_steal')
    op.drop_column('weapon', 'max_attack_fire_steal')
    op.drop_column('weapon', 'min_attack_fire_steal')
    op.drop_column('weapon', 'max_attack_neutral_steal')
    op.drop_column('weapon', 'min_attack_neutral_steal')
    op.drop_column('weapon', 'max_attack_air_damage')
    op.drop_column('weapon', 'min_attack_air_damage')
    op.drop_column('weapon', 'max_attack_earth_damage')
    op.drop_column('weapon', 'min_attack_earth_damage')
    op.drop_column('weapon', 'max_attack_water_damage')
    op.drop_column('weapon', 'min_attack_water_damage')
    op.drop_column('weapon', 'max_attack_fire_damage')
    op.drop_column('weapon', 'min_attack_fire_damage')
    op.drop_column('weapon', 'max_attack_neutral_damage')
    op.drop_column('weapon', 'min_attack_neutral_damage')
    # ### end Alembic commands ###