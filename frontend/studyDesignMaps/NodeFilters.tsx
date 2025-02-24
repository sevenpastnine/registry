import SelectMultiple from './SelectMultiple';
import useStudyDesignMapState from './useStudyDesignMapState';

type OrganisationFilterProps = {
  organisations: Record<string, string>;
};

const OrganisationFilter = ({ organisations }: OrganisationFilterProps) => {
  const setSelectedOrganisationsFilter = useStudyDesignMapState((state) => state.setSelectedOrganisationsFilter);

  return (
    <SelectMultiple
      options={organisations}
      onChange={setSelectedOrganisationsFilter}
      placeholder="Filter by organisation ..."
    />
  );
};

export { OrganisationFilter };
