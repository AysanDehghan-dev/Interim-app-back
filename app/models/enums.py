class JobType:
    """Job type enumeration"""
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACT = "CONTRACT"
    TEMPORARY = "TEMPORARY"
    INTERNSHIP = "INTERNSHIP"
    
    @classmethod
    def get_all(cls):
        return [cls.FULL_TIME, cls.PART_TIME, cls.CONTRACT, cls.TEMPORARY, cls.INTERNSHIP]
    
    @classmethod
    def is_valid(cls, job_type):
        return job_type in cls.get_all()


class ApplicationStatus:
    """Application status enumeration"""
    PENDING = "PENDING"
    REVIEWING = "REVIEWING"
    INTERVIEW = "INTERVIEW"
    REJECTED = "REJECTED"
    ACCEPTED = "ACCEPTED"
    
    @classmethod
    def get_all(cls):
        return [cls.PENDING, cls.REVIEWING, cls.INTERVIEW, cls.REJECTED, cls.ACCEPTED]
    
    @classmethod
    def is_valid(cls, status):
        return status in cls.get_all()
