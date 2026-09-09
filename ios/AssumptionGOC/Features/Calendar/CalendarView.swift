import SwiftUI

struct CalendarView: View {
    @Environment(AppCoordinator.self) private var coordinator
    @State private var viewModel: CalendarViewModel?

    private let columns = Array(repeating: GridItem(.flexible(), spacing: 4), count: 7)
    private let weekdayInitials = ["S", "M", "T", "W", "T", "F", "S"]

    var body: some View {
        Group {
            if let viewModel { content(viewModel) } else { ProgressView() }
        }
        .navigationTitle("Calendar")
        .navigationBarTitleDisplayMode(.inline)
        .task {
            if viewModel == nil { viewModel = coordinator.makeCalendarViewModel() }
            await viewModel?.load()
        }
    }

    @ViewBuilder
    private func content(_ viewModel: CalendarViewModel) -> some View {
        VStack(spacing: 12) {
            header(viewModel)

            HStack(spacing: 4) {
                ForEach(Array(weekdayInitials.enumerated()), id: \.offset) { _, initial in
                    Text(initial)
                        .font(Typography.data(10))
                        .foregroundStyle(.secondary)
                        .frame(maxWidth: .infinity)
                }
            }
            .padding(.horizontal, 16)

            LazyVGrid(columns: columns, spacing: 4) {
                ForEach(0..<viewModel.leadingBlanks, id: \.self) { _ in
                    Color.clear.frame(height: 46)
                }
                ForEach(0..<viewModel.daysInMonth, id: \.self) { index in
                    if let day = viewModel.day(at: index) {
                        CalendarDayCell(day: day) { coordinator.showDay(day.date) }
                    } else {
                        Color.clear.frame(height: 46)
                    }
                }
            }
            .padding(.horizontal, 16)

            if case .failed(let message) = viewModel.state {
                Text(message)
                    .font(Typography.ui(12))
                    .foregroundStyle(.secondary)
                    .padding(.horizontal, 20)
            }
            Spacer()
        }
    }

    private func header(_ viewModel: CalendarViewModel) -> some View {
        HStack {
            Button { Task { await viewModel.step(months: -1) } } label: {
                Image(systemName: "chevron.left")
            }
            Spacer()
            Text(viewModel.monthTitle).font(Typography.display(19))
            Spacer()
            Button { Task { await viewModel.step(months: 1) } } label: {
                Image(systemName: "chevron.right")
            }
        }
        .padding(.horizontal, 20)
    }
}
