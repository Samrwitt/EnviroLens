"""Initial EnviroLens schema with PostGIS geometries.

Revision ID: 001_initial
Revises:
Create Date: 2026-08-05
"""

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry
from sqlalchemy.dialects import postgresql

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    admin_level = postgresql.ENUM(
        "country", "region", "district", "community", name="adminlevel", create_type=False
    )
    sensitivity = postgresql.ENUM(
        "public",
        "internal",
        "restricted",
        "confidential",
        name="sensitivitylevel",
        create_type=False,
    )
    dq_dim = postgresql.ENUM(
        "completeness",
        "validity",
        "consistency",
        "timeliness",
        "uniqueness",
        "geographic_accuracy",
        name="dqdimension",
        create_type=False,
    )
    user_role = postgresql.ENUM(
        "admin", "analyst", "viewer", "data_steward", name="userrole", create_type=False
    )
    bind = op.get_bind()
    for enum_t in (admin_level, sensitivity, dq_dim, user_role):
        enum_t.create(bind, checkfirst=True)

    op.create_table(
        "administrative_areas",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(32), nullable=False, unique=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("level", admin_level, nullable=False),
        sa.Column("parent_id", sa.Integer(), sa.ForeignKey("administrative_areas.id")),
        sa.Column("geometry", Geometry("MULTIPOLYGON", srid=4326)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_administrative_areas_code", "administrative_areas", ["code"])
    op.create_index("ix_administrative_areas_level", "administrative_areas", ["level"])

    op.create_table(
        "communities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(32), nullable=False, unique=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("admin_area_id", sa.Integer(), sa.ForeignKey("administrative_areas.id"), nullable=False),
        sa.Column("geometry", Geometry("MULTIPOLYGON", srid=4326)),
        sa.Column("centroid", Geometry("POINT", srid=4326)),
    )
    op.create_index("ix_communities_code", "communities", ["code"])
    op.create_index("ix_communities_admin_area_id", "communities", ["admin_area_id"])

    op.create_table(
        "reporting_periods",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(32), nullable=False, unique=True),
        sa.Column("label", sa.String(64), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("period_type", sa.String(32), server_default="quarter"),
    )

    op.create_table(
        "data_sources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("dataset_name", sa.String(128), nullable=False, unique=True),
        sa.Column("owning_institution", sa.String(128), nullable=False),
        sa.Column("ministry_or_department", sa.String(128)),
        sa.Column("geographic_coverage", sa.String(128)),
        sa.Column("reporting_frequency", sa.String(64)),
        sa.Column("available_variables", sa.Text()),
        sa.Column("data_format", sa.String(64)),
        sa.Column("sensitivity_level", sensitivity),
        sa.Column("access_method", sa.String(64)),
        sa.Column("data_steward", sa.String(128)),
        sa.Column("data_quality_status", sa.String(64)),
        sa.Column("last_update_date", sa.Date()),
        sa.Column("sharing_restrictions", sa.Text()),
        sa.Column("description", sa.Text()),
    )

    op.create_table(
        "health_facilities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(32), nullable=False, unique=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("facility_type", sa.String(64), server_default="clinic"),
        sa.Column("community_id", sa.Integer(), sa.ForeignKey("communities.id")),
        sa.Column("admin_area_id", sa.Integer(), sa.ForeignKey("administrative_areas.id")),
        sa.Column("location", Geometry("POINT", srid=4326)),
        sa.Column("has_lab_access", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
    )
    op.create_index("ix_health_facilities_code", "health_facilities", ["code"])

    op.create_table(
        "laboratories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(32), nullable=False, unique=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("admin_area_id", sa.Integer(), sa.ForeignKey("administrative_areas.id")),
        sa.Column("location", Geometry("POINT", srid=4326)),
        sa.Column("can_process_respiratory", sa.Boolean(), server_default=sa.text("true")),
    )

    op.create_table(
        "environmental_monitoring_sites",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(32), nullable=False, unique=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("community_id", sa.Integer(), sa.ForeignKey("communities.id")),
        sa.Column("admin_area_id", sa.Integer(), sa.ForeignKey("administrative_areas.id")),
        sa.Column("location", Geometry("POINT", srid=4326)),
        sa.Column("site_type", sa.String(64), server_default="ambient_air"),
    )
    op.create_index("ix_env_sites_code", "environmental_monitoring_sites", ["code"])

    op.create_table(
        "exposure_sources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(32), nullable=False, unique=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("source_type", sa.String(64), server_default="industrial"),
        sa.Column("pollutant", sa.String(64), server_default="PM2.5"),
        sa.Column("admin_area_id", sa.Integer(), sa.ForeignKey("administrative_areas.id")),
        sa.Column("location", Geometry("POINT", srid=4326)),
        sa.Column("estimated_emission_index", sa.Float()),
    )

    op.create_table(
        "environmental_samples",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("site_id", sa.Integer(), sa.ForeignKey("environmental_monitoring_sites.id"), nullable=False),
        sa.Column("period_id", sa.Integer(), sa.ForeignKey("reporting_periods.id")),
        sa.Column("pollutant", sa.String(32), nullable=False),
        sa.Column("value", sa.Float()),
        sa.Column("unit", sa.String(32), server_default="ug/m3"),
        sa.Column("sample_date", sa.Date()),
        sa.Column("data_source_id", sa.Integer(), sa.ForeignKey("data_sources.id")),
        sa.Column("is_valid", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("quality_flag", sa.String(64)),
        sa.UniqueConstraint("site_id", "period_id", "pollutant", "sample_date"),
    )

    op.create_table(
        "health_observations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("facility_id", sa.Integer(), sa.ForeignKey("health_facilities.id"), nullable=False),
        sa.Column("period_id", sa.Integer(), sa.ForeignKey("reporting_periods.id"), nullable=False),
        sa.Column("indicator_code", sa.String(64), nullable=False),
        sa.Column("indicator_name", sa.String(128), nullable=False),
        sa.Column("value", sa.Float()),
        sa.Column("population_at_risk", sa.Float()),
        sa.Column("age_group", sa.String(32)),
        sa.Column("reported_at", sa.Date()),
        sa.Column("data_source_id", sa.Integer(), sa.ForeignKey("data_sources.id")),
        sa.Column("is_valid", sa.Boolean(), server_default=sa.text("true")),
    )

    op.create_table(
        "population_estimates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("community_id", sa.Integer(), sa.ForeignKey("communities.id"), nullable=False),
        sa.Column("period_id", sa.Integer(), sa.ForeignKey("reporting_periods.id"), nullable=False),
        sa.Column("total_population", sa.Integer()),
        sa.Column("under5", sa.Integer()),
        sa.Column("elderly_65plus", sa.Integer()),
        sa.Column("female", sa.Integer()),
        sa.Column("male", sa.Integer()),
        sa.UniqueConstraint("community_id", "period_id"),
    )

    op.create_table(
        "socioeconomic_indicators",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("community_id", sa.Integer(), sa.ForeignKey("communities.id"), nullable=False),
        sa.Column("period_id", sa.Integer(), sa.ForeignKey("reporting_periods.id"), nullable=False),
        sa.Column("indicator_code", sa.String(64), nullable=False),
        sa.Column("indicator_name", sa.String(128), nullable=False),
        sa.Column("value", sa.Float()),
        sa.Column("unit", sa.String(32)),
        sa.UniqueConstraint("community_id", "period_id", "indicator_code"),
    )

    op.create_table(
        "data_quality_issues",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("dataset_name", sa.String(128), nullable=False),
        sa.Column("dimension", dq_dim, nullable=False),
        sa.Column("severity", sa.String(32), server_default="warning"),
        sa.Column("record_ref", sa.String(128)),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("detected_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "data_quality_scores",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("dataset_name", sa.String(128), nullable=False),
        sa.Column("period_code", sa.String(32)),
        sa.Column("completeness", sa.Float(), server_default="0"),
        sa.Column("validity", sa.Float(), server_default="0"),
        sa.Column("consistency", sa.Float(), server_default="0"),
        sa.Column("timeliness", sa.Float(), server_default="0"),
        sa.Column("uniqueness", sa.Float(), server_default="0"),
        sa.Column("geographic_accuracy", sa.Float(), server_default="0"),
        sa.Column("overall", sa.Float(), server_default="0"),
        sa.Column("scored_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("dataset_name", "period_code"),
    )

    op.create_table(
        "risk_indicators",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("community_id", sa.Integer(), sa.ForeignKey("communities.id"), nullable=False),
        sa.Column("period_id", sa.Integer(), sa.ForeignKey("reporting_periods.id"), nullable=False),
        sa.Column("index_code", sa.String(64), server_default="AP_EHRI"),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("risk_band", sa.String(32), nullable=False),
        sa.Column("pm25_component", sa.Float()),
        sa.Column("respiratory_component", sa.Float()),
        sa.Column("proximity_component", sa.Float()),
        sa.Column("vulnerability_component", sa.Float()),
        sa.Column("poverty_component", sa.Float()),
        sa.Column("access_component", sa.Float()),
        sa.Column("completeness_component", sa.Float()),
        sa.Column("methodology_version", sa.String(32), server_default="1.0"),
        sa.Column("calculated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("community_id", "period_id", "index_code"),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("actor", sa.String(128), nullable=False),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("resource", sa.String(128), nullable=False),
        sa.Column("detail", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(64), nullable=False, unique=True),
        sa.Column("role", user_role),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("api_key_hash", sa.String(256)),
    )

    op.create_table(
        "dhis2_sync_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("direction", sa.String(16), nullable=False),
        sa.Column("endpoint", sa.String(128), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("records_count", sa.Integer(), server_default="0"),
        sa.Column("message", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    for table in [
        "dhis2_sync_logs",
        "users",
        "audit_logs",
        "risk_indicators",
        "data_quality_scores",
        "data_quality_issues",
        "socioeconomic_indicators",
        "population_estimates",
        "health_observations",
        "environmental_samples",
        "exposure_sources",
        "environmental_monitoring_sites",
        "laboratories",
        "health_facilities",
        "data_sources",
        "reporting_periods",
        "communities",
        "administrative_areas",
    ]:
        op.drop_table(table)
    sa.Enum(name="userrole").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="dqdimension").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="sensitivitylevel").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="adminlevel").drop(op.get_bind(), checkfirst=True)
