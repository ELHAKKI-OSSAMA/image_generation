from sqlalchemy import Table,Column, Integer,Enum, String, ForeignKey,UniqueConstraint, DateTime, Boolean, NUMERIC, func, Enum, text,JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from datetime import datetime
from database.models.enums import ControlMode, ControlResizeMode,Gendre,ResizeMode
from database.models.base import Base

# Correct association table for many-to-many relationship between SdModelVersion and TypeControl
sdmodelversion_typecontrol_association = Table(
    'sdmodelversion_typecontrol_association',
    Base.metadata,
    Column('sdmodelversion_id', Integer, ForeignKey('sdmodel_versions.id'), primary_key=True),
    Column('typecontrol_id', Integer, ForeignKey('typecontrols.id'), primary_key=True)  # note "typecontrols.id"
)

class SdModelVersion(Base):
    __tablename__ = "sdmodel_versions"
    id = Column(Integer, primary_key=True, index=True)
    version_name = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # One-to-many relationship with SdModel
    sdmodels = relationship("SdModel", back_populates="sdmodel_version")
    # Many-to-many relationship with TypeControl
    type_controls = relationship(
        "TypeControl",
        secondary=sdmodelversion_typecontrol_association,
        back_populates="sdmodel_versions"
    )

class SdModel(Base):
    __tablename__ = "sdmodels"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Foreign key linking to SdModelVersion
    sdmodel_version_id = Column(Integer, ForeignKey("sdmodel_versions.id"), nullable=False)
    # Relationship with SdModelVersion (many-to-one)
    sdmodel_version = relationship("SdModelVersion", back_populates="sdmodels")

class TypeControl(Base):
    __tablename__ = "typecontrols"
    id = Column(Integer, primary_key=True, index=True)
    type_name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    preview_url = Column(String, nullable=False)

    # Many-to-many relationship with SdModelVersion.
    # Note that back_populates must match the attribute name used in SdModelVersion.
    sdmodel_versions = relationship(
        "SdModelVersion",
        secondary=sdmodelversion_typecontrol_association,
        back_populates="type_controls"
    )

    # One-to-many: A TypeControl can be associated with many ControlModels.
    control_models = relationship("ControlModel", back_populates="type_control", cascade="all, delete-orphan")
    # One-to-many: A TypeControl can be associated with many ControlModules.
    control_modules = relationship("ControlModule", back_populates="type_control", cascade="all, delete-orphan")


# Third table
class ControlModel(Base):
    __tablename__ = "controlmodels"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


    # Each ControlModel has one TypeControl.
    typecontrol_id = Column(Integer, ForeignKey("typecontrols.id"), nullable=False)
    type_control = relationship("TypeControl", back_populates="control_models")

    

class ControlModule(Base):
    __tablename__ = "controlmodules"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)

    created_at = Column(DateTime, server_default=func.now())


    # Each ControlModule has one TypeControl.
    typecontrol_id = Column(Integer, ForeignKey("typecontrols.id"), nullable=False)
    type_control = relationship("TypeControl", back_populates="control_modules")


model_controlnet_association = Table(
    'model_controlnet_association',
    Base.metadata,
    Column('model_id', Integer, ForeignKey('models.id'), primary_key=True),
    Column('controlnet_id', Integer, ForeignKey('controlnet.id'), primary_key=True)
)

class ControlNet(Base):
    __tablename__ = "controlnet"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    enabled = Column(Boolean, nullable=False, default=False)
    guidance_start = Column(NUMERIC(precision=4, scale=2), nullable=False, default=0.0)
    guidance_end = Column(NUMERIC(precision=4, scale=2), nullable=False, default=1.0)
    weight = Column(NUMERIC(precision=4, scale=2), nullable=False, default=1.0)
    control_mode = Column(Enum(ControlMode), default=ControlMode.BALANCED)
    resize_mode = Column(Enum(ControlResizeMode), default=ControlResizeMode.JUSTRESIZE)

    # Each ControlNet has one ControlModel.
    control_model_id = Column(Integer, ForeignKey("controlmodels.id"), nullable=False)
    control_model = relationship("ControlModel", backref="controlnets")
    
    # Each ControlNet has one ControlModule.
    control_module_id = Column(Integer, ForeignKey("controlmodules.id"), nullable=False)
    control_module = relationship("ControlModule", backref="controlnets")
    

    # Remove the previous model_id relationship
    # Instead, add the many-to-many relationship with Model:
    models = relationship(
        "Model",
        secondary=model_controlnet_association,
        back_populates="controlnets"
    )

    @property
    def type_control(self):
        """
        Returns the common TypeControl for this ControlNet, but first verifies that
        the associated ControlModel and ControlModule share the same TypeControl.
        """
        tc_model = self.control_model.type_control
        tc_module = self.control_module.type_control
        if tc_model.id != tc_module.id:
            raise ValueError("Inconsistent TypeControl: ControlModel and ControlModule do not match!")
        return tc_model

    def has_model_sdmodel_version(self, model_instance):
        """
        Given a Model instance, checks whether the model's SdModelVersion is
        among the SdModelVersions associated with this ControlNet's TypeControl.
        """
        return model_instance.sdmodel.sdmodel_version in self.type_control.sdmodel_versions

class SamplerTypeTable(Base):
    __tablename__ = "samplertypes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

class SamplerModeTable(Base):
    __tablename__ = "samplermodes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

class ModelCategoryTable(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

class Model(Base):
    __tablename__ = "models"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    preview_url = Column(String, nullable=False)
    type = Column(String, nullable=True)
    gendre = Column(Enum(Gendre),default=Gendre.BOTH)
    prompt = Column(String, nullable=True)
    negative_prompt = Column(String, nullable=True)
    resize_mode = Column(Enum(ResizeMode), default=ResizeMode.JUSTRESIZE)
    steps = Column(Integer, nullable=True)
    save_images = Column(Boolean, nullable=True)
    seed = Column(Integer, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    cfg_scale = Column(NUMERIC(precision=4, scale=2), nullable=False, default=1.0)
    created_at = Column(DateTime, server_default=func.now())

    

    # Each Model is linked to one SdModel.
    sdmodel_id = Column(Integer, ForeignKey("sdmodels.id"), nullable=False)
    sdmodel = relationship("SdModel", backref="models")
    
    # Each Model has one SamplerMode and one SamplerType.
    sampler_mode_id = Column(Integer, ForeignKey("samplermodes.id"), nullable=False)
    sampler_mode = relationship("SamplerModeTable")
    sampler_type_id = Column(Integer, ForeignKey("samplertypes.id"), nullable=False)
    sampler_type = relationship("SamplerTypeTable")

    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)
    category = relationship("ModelCategoryTable")

    
    # Instead of a one-to-many on ControlNet via model_id, we now define a many-to-many.
    controlnets = relationship(
        "ControlNet",
        secondary=model_controlnet_association,
        back_populates="models"
    )

    @property
    def current_sdmodel_version(self):
        """
        Convenience property to return this model's SdModelVersion,
        obtained from the associated SdModel.
        """
        return self.sdmodel.sdmodel_version

    @property
    def valid_controlnet_associations(self):
        """
        Checks that for each ControlNet associated with this Model,
        the Model’s current SdModelVersion is present in the ControlNet's
        TypeControl-s' collection of SdModelVersions.
        
        Returns True if the condition is met for all controlnets; otherwise False.
        """
        # Iterate over controlnets in this model.
        for controlnet in self.controlnets:
            if self.current_sdmodel_version not in controlnet.type_control.sdmodel_versions:
                return False
        return True

    def validate_controlnet_associations(self):
        """
        Optionally, raise an exception if any associated ControlNet does not contain
        the Model's SdModelVersion in its TypeControl.
        """
        for controlnet in self.controlnets:
            if self.current_sdmodel_version not in controlnet.type_control.sdmodel_versions:
                raise ValueError(
                    f"The SdModelVersion '{self.current_sdmodel_version.version_name}' "
                    f"of Model '{self.name}' is not present in the TypeControl '{controlnet.type_control.type_name}' "
                    f"associated with ControlNet '{controlnet.name}'."
                )
